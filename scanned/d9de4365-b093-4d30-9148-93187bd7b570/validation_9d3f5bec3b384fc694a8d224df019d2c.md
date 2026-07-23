Looking at the RubiconRouter bug class: a caller-supplied external contract address is trusted without factory validation, allowing a malicious contract to return the router's own balance as the withdrawal amount, draining it. I need to find the same pattern in Metric OMM.

Let me trace the `MetricOmmPoolLiquidityAdder` callback settlement path carefully.