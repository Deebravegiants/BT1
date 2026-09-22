# [M] zBanc - outdated fork

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

According to the client the system was forked off bancor [v0.6.18 (Oct 2020)](https://github.com/bancorprotocol/contracts-solidity/releases/tag/v0.6.18). The current version 0.6.x is [v0.6.36 (Apr 2021)](https://github.com/bancorprotocol/contracts-solidity/releases/tag/v0.6.36).

#### Recommendation

It is recommended to check if relevant security fixes were released after v0.6.18 and it should be considered to rebase with the current stable release.
