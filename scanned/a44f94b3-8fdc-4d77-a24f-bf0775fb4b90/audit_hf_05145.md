# [M] The RiskParameter.liquidationFee variable is

## Summary
Severity: Medium
Contest weight: 0.2475
Dataset id: 23201
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In Perennial v2.3, it became a percentage value. However, this change is not fully reflected in the code.
from the ProtocolParameter struct, leading to incorrect assumptions, particularly regarding the protocol-wide maxFeeAbsolute setting, as well as per-market minMaintenance values.
As stated in the README in the section, "Please list any known issues and explicitly state the acceptable risks for each known issue.":
Coordinators are given broad control over the parameters of the markets they coordinate. The protocol parameter is designed to prevent situations where parameters are set to maliciously steal funds. If the coordinator can operate within the bounds of reasonable protocol parameters to negatively affect markets, we would like to know about it.
There is theoretically no limitation on the liquidationFee value. The liquidation fee that can be paid by the account can exceed the maxFeeAbsolute value, breaking assumptions and negatively affecting the markets.
For example, if the maxFeeAbsolute value is set to $50, then the liquidationFee can be up to 5000% of the settlement fee, calculated using this equation:
File: VersionLib.sol
246: function _accumulateLiquidationFee(
247:     Version memory next,
248:     VersionAccumulationContext memory context
249: )
250:     internal
251:     pure
252:     returns (uint256 liquidationFee)
253: {
254:     liquidationFee = context.toOracleVersion.valid ?
255:         context.toOracleReceipt.settlementFee.mul(context.riskParameter.liquidationFee) :
256:         0;
257: }
Here are the places where the liquidationFee percentage value is incorrectly validated:
File: RiskParameter.sol
139: if (self.liquidationFee.gt(protocolParameter.maxFeeAbsolute)) revert RiskParameterStorageInvalidError();
File: RiskParameter.sol
155: if (self.minMaintenance.lt(self.liquidationFee)) revert RiskParameterStorageInvalidError();
• Coordinators can negatively affect markets while operating within the bounds of reasonable protocol parameters.

## Recommendation
The protocol-wide maxFeeAbsolute value needs to be enforced across the markets.
The liquidationFee should be validated as a percentage value.
