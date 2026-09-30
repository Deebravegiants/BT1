# [H] accounting::setminimumjrtsrtratio sets reservebps instead of minimumjrtsrtratio making ratio configuration impossible

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23358
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Description: The Accounting::setMinimumJrtSrtRatio function contains a an implementation error where it modifies the wrong state variable. Instead of setting minimumJrtSrtRatio, the function incorrectly sets reserveBps, making it impossible to configure the minimum Junior-to-Senior tranche ratio.

```solidity
function setMinimumJrtSrtRatio (uint256 bps) external onlyOwner {
    require(bps <= RESERVE_BPS_MAX, "ReserveBpsMax");
    reserveBps = bps;
    emit ReservePercentageChanged(reserveBps);
}
```

Impact: Impossible Risk Parameter Configuration: The minimumJrtSrtRatio variable can only be set during initialization (currently hardcoded to 5%) and cannot be updated afterward, preventing proper risk management adjustments.  
Accidental Reserve Configuration: Calling setMinimumJrtSrtRatio thinking it will adjust tranche ratios will instead modify the reserve percentage, leading to unintended reserve allocation changes.

## Recommendation
Recommended Mitigation: Perform the following changes inside the Accounting contract:

```solidity
event MinimumJrtSrtRatioChanged(uint256 minimumJrtSrtRatio);
function setMinimumJrtSrtRatio (uint256 bps) external onlyOwner {
-    require(bps <= RESERVE_BPS_MAX, "ReserveBpsMax");
-    reserveBps = bps;
-    emit ReservePercentageChanged(reserveBps);
+    require(bps <= 1e18, "InvalidRatio"); // Max 100%
+    minimumJrtSrtRatio = bps;
+    emit MinimumJrtSrtRatioChanged(minimumJrtSrtRatio);
}
```
