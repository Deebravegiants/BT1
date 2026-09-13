# [H] \[H03\] Inconsistent use of oracles

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Throughout the protocol, oracles are relied upon to keep FEI stable, calculate payouts to users, and judge whether actions are eligible to be carried out. In addition to the vulnerabilities caused by oracles described in [C01](#c01), and [H01](#h01), we found the use of oracles throughout the code to be inconsistent and confusing.
