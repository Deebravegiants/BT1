# [C] Malicious Package in bitcoin-sweep

## Summary
Severity: Critical
Chain: bitcoin-sweep
Component: bitcoin-sweep
CWE: Embedded Malicious Code
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-8hqw-qp6r-vqcm
Type: github-advisory

## Details
All versions of this package contained malware. The package was designed to find and exfiltrate cryptocurrency wallets.


## Recommendation

Any computer that has this package installed or running should be considered fully compromised. All secrets and keys stored on that computer should be rotated immediately from a different computer.

The package should be removed, but as full control of the computer may have been given to an outside entity, there is no guarantee that removing the package will remove all malicious software resulting from installing it.
