# [C] New subGauges can't be used by the protocol

## Summary
Severity: Critical
Contest weight: 0.0465
Dataset id: 16308
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The createSubGauge method in GaugeFactory creates a new subGauge but does not actually add the subGauge to the GaugeProxy as it is done in createGaugeProxyAndSubGauges . Even though the GaugeProxy contract has an addSubGauge method, it is only callable by the gaugeFactory or by the TLSDFactory . Neither contracts have an actual way to directly call the addSubGauge method, which means that even though you can create new subGauge s you can't actually add them to the GaugeProxy in any way.

## Recommendation
Change the createSubGauge method to execute the same GaugeProxy(_gaugeProxy).addSubGauge(_stakingTokens[i], subGauge); call as in createGaugeProxyAndSubGauges with the given _stakingToken argument.
