# [M] GFA token incident: The GFA token was exploited on the BNB chain, which resulted in a loss of assets worth approximately $15,000. The root cause of th

## Summary
Severity: Medium
Target: GFA token
Loss: $ 15,000
Attack method: Contract Vulnerability
Published: 2024-04-14
Source: https://bscscan.com/tx/0xe15d6f7fa891c2626819209edf2d5ded6948310eaada067b400062aa022ce718
Type: slowmist-incident

## Details
The GFA token was exploited on the BNB chain, which resulted in a loss of assets worth approximately $15,000. The root cause of the exploit is a lack of access control. The vulnerable contracts had functions for calculating rewards, for which anyone could invoke a call to them. The hacker was able to manually calculate and generate the rewards and drain the tokens. The exploiter has already laundered the stolen assets into Tornado Cash.
