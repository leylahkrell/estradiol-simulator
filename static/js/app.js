const updatePlot = async () => {
    const estradiolType = document.getElementById('estradiol-type').value;
    const concentration = parseFloat(document.getElementById('concentration').value);
    const dose = parseFloat(document.getElementById('dose').value);
    const frequency = parseFloat(document.getElementById('frequency').value);
    const days = parseInt(document.getElementById('days').value);
    const bodyWeight = parseFloat(document.getElementById('body-weight').value);
    const initialState = document.querySelector('input[name="initial-state"]:checked').value;
    const showReference = document.getElementById('show-reference').checked;

    const response = await fetch('/update-plot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            estradiol_type: estradiolType,
            concentration: concentration,
            dose: dose,
            frequency: frequency,
            days: days,
            body_weight: bodyWeight,
            initial_state: initialState,
            show_reference: showReference
        }),
    });

    const data = await response.json();
    let { time_days, levels_pg_ml, max_level, min_level, ref_days, ref_e2 } = data;


    const plotDiv = document.getElementById('plot');
    const plotData = [];

    // Add the target range area FIRST (so it's underneath other elements)
    const targetMin = parseFloat(document.getElementById('target-min').value);
    const targetMax = parseFloat(document.getElementById('target-max').value);

    // Add the target range area with hover disabled
    plotData.push({
        x: [...time_days, ...time_days.reverse()],
        y: [...Array(time_days.length).fill(targetMax), ...Array(time_days.length).fill(targetMin).reverse()],
        fill: 'toself',
        fillcolor: 'rgba(152, 76, 175, 0.2)',
        line: { color: 'rgba(175, 76, 175, 0.4)' },
        name: 'Target Range',
        hoverinfo: 'skip',  // This prevents the target range from capturing hover events
        hoveron: 'fills'    // This restricts hover to just the fill area
    });

    // Add the cis female reference line if showReference is true
    if (showReference) {
        plotData.push({
            x: ref_days,
            y: ref_e2,
            mode: 'lines',
            name: 'Cis Female Ref',
            line: { color: '#a041ff', width: 2, dash: 'dot' },
            hoverinfo: 'x+y',
            hovertemplate: 'Time: %{x:.2f} days<br>Level: %{y:.0f} pg/mL<extra></extra>'
        });
    }

    // Add the estradiol levels over time curve
    plotData.push({
        // Reverse the x-axis to fix reversed time.
        // TODO Fix root cause of the issue.
        x: time_days.reverse(), 
        y: levels_pg_ml,
        mode: 'lines',
        name: 'Estradiol Levels',
        line: {
            color: 'rgb(0, 151, 238)',
            width: 2,
            shape: 'linear',
            connectgaps: true
        },
        hoverinfo: 'x+y',
        hovertemplate: 'Time: %{x:.2f} days<br>Level: %{y:.0f} pg/mL<extra></extra>'

    });

    const injectionTimes = Array.from(
        { length: Math.floor(days / frequency) + (days % frequency >= 0 ? 1 : 0)},
        (_, i) => i * frequency
    );
    const injectionLevels = Array(injectionTimes.length).fill(0);

    // Mark injection times on the plot
    plotData.push({
        x: injectionTimes,
        y: injectionLevels,
        mode: 'markers',
        name: 'Injections',
        marker: { symbol: 'triangle-up', size: 12, color: '#ff00ff' },
        hoverinfo: 'x',
        hovertemplate: 'Day %{x}<extra></extra>',
    });

    // graph design and labels
    const layout = {
        title: `Estradiol Levels for ${(concentration * dose).toFixed(1)} mg estradiol ${estradiolType}, as ${dose.toFixed(2)} mL injection, every ${frequency} days`,
        xaxis: { 
            title: 'Time (days)',
            range: [0, days],
            fixedrange: true,
            gridcolor: '#281f3f',
            zerolinecolor: '#3d2856'
        },
        yaxis: { 
            title: 'Estradiol Level (pg/mL)',
            gridcolor: '#281f3f',
            zerolinecolor: '#3d2856'
        },
        showlegend: true,
        margin: { l: 60, r: 20, t: 60, b: 70 },
        // Dark theme properties
        paper_bgcolor: '#06030c',
        plot_bgcolor: '#110d1d',
        font: {
            family: 'Noto Sans, Arial, sans-serif',
            color: '#ffffff'
        },
        legend: {
            bgcolor: 'rgba(6, 3, 12, 0.7)',
            bordercolor: '#281f3f',
            yanchor: 'top',
            y: 0.98,
            xanchor: 'right',
            x: 0.99,
            orientation: 'v',
            traceorder: 'normal',
            font: {
                size: 12
            }
        }
    };

    // Configuration to customize the mode bar
    const config = {
        modeBarButtonsToRemove: [
            'zoomIn2d', 'zoomOut2d', 'zoom2d', 'pan2d', 
            'select2d', 'lasso2d', 'autoScale2d',
            'resetScale2d', 'hoverClosestCartesian', 
            'hoverCompareCartesian', 'toggleSpikelines'
        ],
        displaylogo: false,
    };

    Plotly.newPlot(plotDiv, plotData, layout, config);

    document.getElementById('max-level').innerText = `Peak level: ${max_level.toFixed(1)} pg/mL`;
    document.getElementById('min-level').innerText = `Trough level: ${min_level.toFixed(1)} pg/mL`;
};

// Add these event listeners to all form inputs
document.querySelectorAll('select, input').forEach(element => {
    element.addEventListener('change', updatePlot);
});

// Call updatePlot once on page load to show initial plot
document.addEventListener('DOMContentLoaded', () => {
    updatePlot();
});