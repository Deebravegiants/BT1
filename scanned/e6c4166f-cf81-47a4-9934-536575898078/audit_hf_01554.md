# [M] No method to withdraw from EtherFi

## Summary
Severity: Medium
Contest weight: 0.0813
Dataset id: 8303
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The YieldStrategy.sol contract has the method depositWETHInEtherfi that allows the caller to deposit WETH into EtherFi to obtain WEETH.
However, there is currently no method to do the opposite...withdraw the underlying WETH by redeeming the WEETH. As such, the only way to regain the original WETH is to swap via 1INCH, but this depends entirely on the available liquidity in the relevant pools required in the path from WEETH to WETH. I'm not sure why we wouldn't want the withdraw equivalent like we have for sDAI and Pendle.

## Recommendation
Add a withdrawWETHInEtherfi method.
