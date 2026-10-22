# [M] GovNFT: maxBridge has no effect

## Summary
Severity: Medium
Contest weight: 0.3765
Dataset id: 17355
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In GovNFT, setMaxBridge function is provided to set maxBridge, but this variable is not used, literally it should be used to limit the number of GovNFTs crossing chain, but it doesn’t work in GovNFT.

```solidity
uint256 public maxBridge = 20;
...
function setMaxBridge(uint256 _max) external onlyOwner {
    maxBridge = _max;
}
```

## Recommendation
Consider applying the maxBridge variable.

The Warden has shown how, an unused variable, which was meant to cap the amount of tokens bridged per call, could cause a DOS.

These types of DOS could only be fixed via Governance Operations, and could create further issues, for this reason I agree with Medium Severity.

Mitigation: <https://github.com/code-423n4/2022-12-tigris/pull/2#issuecomment-1419175169>
