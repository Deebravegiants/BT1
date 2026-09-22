# [H] CL-2020-11: py\_ecc arbitrary signature verification bypass

## Summary
Severity: High
Chain: Ethereum (consensus layer)
Component: None
Published: 2021-12-01
Source: https://github.com/ethereum/public-disclosures/blob/master/disclosures/CL-2021-12-01.md
Type: ef-disclosure

## Details
Affected Clients: None
Uid: CL-2020-11
Bug: py\_ecc arbitrary signature verification bypass
Type: Crypto
Summary: In elliptic curves, the most dangerous point is infinity O. This is because xO = O for all x which means that all arithmetic verification becomes trivially satisfied. Therefore, checking for infinity is crucial. py\_cc checks for infinity but the check is not accurate
Links: [](https://github.com/ethereum/py_ecc/pull/107)[https://github.com/ethereum/py\_ecc/pull/107](https://github.com/ethereum/py_ecc/pull/107)
Reported: 2020-11-13
Fixed Date: 2020-11-16
Published: 2021-12-01
Severity: High
Bounty Hunter: Quan
Bounty Points: 5000
Bounty Reward (Usd): 10000
