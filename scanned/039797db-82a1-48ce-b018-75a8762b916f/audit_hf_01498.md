# [H] H-5 athleteSecondarySalesBPS and fantiumSecondarySalesBPS should be restricted

## Summary
Severity: High
Contest weight: 0.1302
Dataset id: 7950
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
athleteSecondarySalesBPS and fantiumSecondarySalesBPS should be restricted because they
will be used in other contracts to calculate royalties with base point = 1 / 10_000, so if
athleteSecondarySalesBPS + fantiumSecondarySalesBPS > 10_000, the royalty will be >
100%. Due to this all transactions with royalty payments will revert.
FantiumNFTV3.sol#L526-L527
FantiumNFTV3.sol#L544-L545
FantiumNFTV3.sol#L658-L659
FantiumNFTV3.sol#L752-L753

## Recommendation
We recommend adding the following check: _athleteSecondarySalesBPS +
fantiumSecondarySalesBPS <= 10000.
