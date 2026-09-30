# [M] Standard deviation calculation

## Summary
Severity: Medium
Contest weight: 0.1089
Dataset id: 23056
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The estimation of the regrets & time steps scores will be based because of a biased estimator.
The function StdDev calculates the sample standard deviation of an arbitrary data vector. To do so, it uses the formula sqrt((Σ(x-￿))̂2/N). Because the data is also used to
calculate the sample mean, this estimator will be biased, i.e. its expectation value will
not be ￿, but rather sqrt((n - 1)/n) ￿.
The utility function is used in synth_palette_weight.go to get the std. deviation of the regrets and in rewards_internal.go to get the std. deviation of the latest time steps scores.
The std. deviation estimate in the two mentioned places will be slightly off, leading to a wrong estimate.

## Recommendation
Apply Bessel's correction, i.e. divide by N-1 instead of N, which means subtracting one from lenData in the code.
