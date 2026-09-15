# [M] Salt's file contents overwrite the VirtKey class

## Summary
Severity: Medium
Advisory: GHSA-7f3f-x5f5-79gw
CVE: CVE-2025-22241
CWE: CWE-22, CWE-73
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-06-13
Source: https://github.com/advisories/GHSA-7f3f-x5f5-79gw
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=3007.0rc1 <3007.4
- PyPI: `salt` — affected >=3006.0rc1 <3006.12

## Details
File contents overwrite the VirtKey class is called when “on-demand pillar” data is requested and uses un-validated input to create paths to the “pki directory”. The functionality is used to auto-accept Minion authentication keys based on a pre-placed “authorization file” at a specific location and is present in the default configuration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-22241
- https://github.com/saltstack/salt/commit/9445f496fed61b15dc4364818007e5b765b0746f
- https://docs.saltproject.io/en/3006/topics/releases/3006.12.html
- https://docs.saltproject.io/en/3007/topics/releases/3007.4.html
- https://github.com/saltstack/salt
