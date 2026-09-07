# [H] Routinator has cache path traversal when processing the module component of rsync URIs

## Summary
Severity: High
Advisory: GHSA-33mj-99mg-8g73
CVE: CVE-2026-49233
CWE: CWE-22
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-33mj-99mg-8g73
Type: github-advisory

## Affected
- crates.io: `routinator` — affected >=0 <0.15.2

## Details
Routinator does not properly check the module component of rsync URIs, which are used to create the file system paths for the Routinator cache. This allows for path traversal by having a module name containing .., potentially providing an attacker access to the entire Routinator rsync cache.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-49233
- https://github.com/NLnetLabs/routinator
- https://github.com/NLnetLabs/routinator/releases/tag/v0.15.2
- https://www.nlnetlabs.nl/downloads/routinator/CVE-2026-49233.txt
