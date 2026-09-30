# [M] The default value of epsilon dif-

## Summary
Severity: Medium
Contest weight: 0.1042
Dataset id: 23052
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The default value of epsilon differs from what is stated in the whitepaper
According to docs
We ask that auditors look for both typical security vulnerabilities, but also departures of the codebase from the intentions defined in the whitepaper.
together as defined in the whitepaper. This requires an understanding of the math of the whitepaper, which we urge auditors to develop.
Epsilon:
alloraMath.MustNewDecFromString("0.0001")
x/emissions/types/params.go#L24
stdDevRegretsPlusMedianTimesFTolerancePlusEpsilon, err := stdDevRegretsPlusMedianTimesFTolerance.Add(p.Epsilon)
s/keeper/inference_synthesis/synth_palette_weight.go#L46
Precision will be tight

## Recommendation
-Epsilon: alloraMath.MustNewDecFromString("0.0001")
+Epsilon: alloraMath.MustNewDecFromString("0.01")
