# [M] Remote P2P Crash Vulnerability

## Summary
Severity: Medium
Chain: Stellar
Component: stellar/stellar-core
CVE: CVE-2024-32985
Published: 2024-05-09
Source: https://github.com/stellar/stellar-core/security/advisories/GHSA-mgx8-frjx-x33m
Type: github-advisory

## Details
### Impact
Core nodes were not handling the failure mode of a 3rd party library properly. This meant that these core nodes could be randomly crashed due to a race condition because of not handling the failure mode. The likelihood of this vulnerability affecting the entire network of core nodes is low since the crashed node come back up online right away.

### Was this exploited?
No, there were attempts but core nodes were able to handle it gracefully since the scale of the attack was low.

### Patches
Code fix mitigation is part of core v20.4.0 release
