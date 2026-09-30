# [M] ABCCApp incident: ABCCApp on BSC was reportedly attacked, resulting in a loss of approximately $10.1K.

The root cause was that the contract’s add

## Summary
Severity: Medium
Target: ABCCApp
Loss: $ 10,100
Attack method: Contract Vulnerability
Published: 2025-08-23
Source: https://bscscan.com/tx/0xee4eae6f70a6894c09fda645fb24ab841e9847a788b1b2e8cb9cc50c1866fb12
Type: slowmist-incident

## Details
ABCCApp on BSC was reportedly attacked, resulting in a loss of approximately $10.1K.

The root cause was that the contract’s addFixedDay() function lacked access control, and fixedDay was used in calculating claimable USDT.
