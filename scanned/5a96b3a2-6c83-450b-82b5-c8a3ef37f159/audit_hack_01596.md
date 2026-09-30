# [M] CherryFi incident: The transfer logic of TRON's DeFi project CherryFi calls the safeTransfer function to perform specific transfer operations. Howeve

## Summary
Severity: Medium
Target: CherryFi
Loss: -
Attack method: Contract Vulnerability
Published: 2020-09-06
Source: https://www.quadrigainitiative.com/hackfraudscam/cherryficontractvulnerabilities.php
Type: slowmist-incident

## Details
The transfer logic of TRON's DeFi project CherryFi calls the safeTransfer function to perform specific transfer operations. However, the USDT transfer logic does not return a value, which causes the safeTransfer call to never succeed, which leads to the lockup of funds, and therefore users cannot perform USDT transfers in and out. It is understood that the CherryFi code has not been audited.
