# [H] All curve params should be signed by the schnorr private key in the proof, or users may be griefed

## Summary
Severity: High
Contest weight: 0.0940
Dataset id: 15193
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An example of this issue is for example here. If the last bit of isLegacy is 0, it checks address(this).balance, otherwise it IERC20(_WETH_ADDRESS).balanceOf(address(this)). This means that if for the same pool, the wrong isLegacy is used, 0 outAmounts[i] will be recorded.

## Recommendation
Either send the curve params in the proof and sign them with the schnorr private key or set a mapping from pool to the correct pool params.
