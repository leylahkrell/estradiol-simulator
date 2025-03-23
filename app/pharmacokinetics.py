from fastapi import APIRouter
import numpy as np

router = APIRouter()

ESTRADIOL_TYPES = {
    'valerate': {'absorption_half_life': 1.5, 'elimination_half_life': 3.5},
    'cypionate': {'absorption_half_life': 1.5, 'elimination_half_life': 8.0},
    'enanthate': {'absorption_half_life': 1.5, 'elimination_half_life': 10.0}
}
ESTER_TO_ESTRADIOL = {
    'valerate': 0.76,
    'cypionate': 0.72,
    'enanthate': 0.70
}
BIOAVAILABILITY = 0.85
MG_TO_PG_CONVERSION = 1e9
L_TO_ML_CONVERSION = 1000
VOLUME_OF_DISTRIBUTION = 120.0

def calculate_rate_constants(estradiol_type):
    absorption_half_life = ESTRADIOL_TYPES[estradiol_type]['absorption_half_life']
    elimination_half_life = ESTRADIOL_TYPES[estradiol_type]['elimination_half_life']
    k_absorption = np.log(2) / absorption_half_life
    k_elimination = np.log(2) / elimination_half_life
    return k_absorption, k_elimination

def calculate_estradiol_levels(concentration_mg_ml,
                               dose_ml,
                               days,
                               k_absorption,
                               k_elimination,
                               body_weight,
                               estradiol_type,
                               time_points=100):
    dose_mg = concentration_mg_ml * dose_ml
    ester_conversion = ESTER_TO_ESTRADIOL[estradiol_type]
    dose_pg = dose_mg * ester_conversion * BIOAVAILABILITY * MG_TO_PG_CONVERSION
    time_days = np.linspace(0, days, time_points)
    distribution_volume = VOLUME_OF_DISTRIBUTION * body_weight
    levels_pg_ml = ((dose_pg / distribution_volume / L_TO_ML_CONVERSION)
                    * (k_absorption / (k_absorption - k_elimination))
                    * (np.exp(-k_elimination * time_days)
                       - np.exp(-k_absorption * time_days)))
    return time_days, levels_pg_ml

def calculate_multiple_doses(concentration_mg_ml, dose_ml,
                             frequency_days, total_days,
                             k_absorption, k_elimination,
                             body_weight, estradiol_type,
                             initial_state='new',
                             time_points=1000):
    time_days = np.linspace(0, total_days, time_points)
    levels_pg_ml = np.zeros_like(time_days)

    if initial_state == 'steady':
        elimination_half_life = ESTRADIOL_TYPES[estradiol_type]['elimination_half_life']
        lookback_days = elimination_half_life * 5
        lookback_doses = int(np.ceil(lookback_days / frequency_days))
        extended_days = lookback_days + total_days
        extended_time = np.linspace(-lookback_days, total_days,
                                    int(time_points * extended_days / total_days))
        extended_levels = np.zeros_like(extended_time)
        all_dose_times = np.arange(-frequency_days * lookback_doses,
                                   total_days + 0.1, frequency_days)

        for dose_time in all_dose_times:
            relative_time = extended_time - dose_time
            mask = relative_time >= 0
            if not any(mask):
                continue
            dose_relative_time = relative_time[mask]
            dose_mg = concentration_mg_ml * dose_ml
            ester_conversion = ESTER_TO_ESTRADIOL[estradiol_type]
            dose_pg = dose_mg * ester_conversion * BIOAVAILABILITY * MG_TO_PG_CONVERSION
            distribution_volume = VOLUME_OF_DISTRIBUTION * body_weight
            dose_contribution = ((dose_pg / distribution_volume / L_TO_ML_CONVERSION)
                                 * (k_absorption / (k_absorption - k_elimination))
                                 * (np.exp(-k_elimination * dose_relative_time)
                                    - np.exp(-k_absorption * dose_relative_time)))
            extended_levels[mask] += dose_contribution

        start_idx = np.argmin(np.abs(extended_time))
        visible_indices = np.arange(start_idx, start_idx + time_points)
        if len(visible_indices) > len(extended_levels):
            visible_indices = visible_indices[:len(extended_levels)]
        levels_pg_ml = extended_levels[visible_indices]
    else:
        dose_times = np.arange(0, total_days + 0.1, frequency_days)
        for dose_time in dose_times:
            relative_time = time_days - dose_time
            mask = relative_time >= 0
            if not any(mask):
                continue
            _, dose_levels = calculate_estradiol_levels(concentration_mg_ml,
                                                                      dose_ml,
                                                                      total_days - dose_time,
                                                                      k_absorption,
                                                                      k_elimination,
                                                                      body_weight,
                                                                      estradiol_type,
                                                                      sum(mask))
            levels_pg_ml[mask] += dose_levels
    return time_days, levels_pg_ml

def generate_menstrual_reference(days_to_simulate):
    # Create a standard 28-day menstrual cycle pattern
    cycle_length = 28
    days_in_cycle = np.linspace(0, cycle_length, 100)

    # Model the biphasic estradiol pattern
    # Early follicular phase (low)
    # Mid-follicular (rising)
    # Pre-ovulatory peak
    # Luteal phase plateau with gradual decline

    cycle_e2 = np.zeros_like(days_in_cycle)

    # Days 1-5 (menstruation): 30-100 pg/mL
    mask1 = days_in_cycle < 5
    cycle_e2[mask1] = 30 + 70 * days_in_cycle[mask1]/5

    # Days 5-12 (follicular phase): rising from 50-200 pg/mL
    mask2 = (days_in_cycle >= 5) & (days_in_cycle < 12)
    cycle_e2[mask2] = 100 + 100 * (days_in_cycle[mask2]-5)/7

    # Days 12-14 (ovulation): peak at 200-400 pg/mL
    mask3 = (days_in_cycle >= 12) & (days_in_cycle < 14)
    cycle_e2[mask3] = 200 + 200 * np.sin(np.pi * (days_in_cycle[mask3]-12)/2)

    # Days 14-24 (luteal phase): 100-300 pg/mL plateau
    mask4 = (days_in_cycle >= 14) & (days_in_cycle < 24)
    cycle_e2[mask4] = 400 - 100 * (days_in_cycle[mask4]-14)/10

    # Days 24-28 (late luteal phase): declining to baseline
    mask5 = days_in_cycle >= 24
    cycle_e2[mask5] = 300 - 250 * (days_in_cycle[mask5]-24)/4

    # Repeat the pattern for the requested simulation duration
    cycles_needed = int(np.ceil(days_to_simulate / cycle_length))
    full_days = np.linspace(0, cycles_needed * cycle_length, 100 * cycles_needed)
    full_e2 = np.tile(cycle_e2, cycles_needed)

    # Trim to the requested simulation days
    mask = full_days <= days_to_simulate
    return full_days[mask], full_e2[mask]
