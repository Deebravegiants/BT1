# [M] Use of Uninitialized Variable in trilogy

## Summary
Severity: Medium
Advisory: GHSA-5g4r-2qhx-vqfm
CVE: CVE-2022-31026
CWE: CWE-908
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-06-06
Source: https://github.com/advisories/GHSA-5g4r-2qhx-vqfm
Type: github-advisory

## Affected
- RubyGems: `trilogy` — affected >=0 <2.1.1

## Details
### Impact

When authenticating, a malicious server could return a specially crafted authentication packet, causing the client to read and return up to 12 bytes of data from an uninitialized variable in stack memory.

### Patches

Users of the trilogy gem should upgrade to version 2.1.1

### Workarounds

This issue can be avoided by only connecting to trusted servers.

### Acknowledgements 

We would like to thank Sergei Volokitin for reporting this vulnerability

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [trilogy](https://github.com/github/trilogy)

## References
- https://github.com/github/trilogy/security/advisories/GHSA-5g4r-2qhx-vqfm
- https://nvd.nist.gov/vuln/detail/CVE-2022-31026
- https://github.com/github/trilogy/commit/6bed62789eaf119902b0fe247d2a91d56c31a962
- https://github.com/github/trilogy
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/trilogy/CVE-2022-31026.yml
