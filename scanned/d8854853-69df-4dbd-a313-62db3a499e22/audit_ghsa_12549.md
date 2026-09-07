# [M] Teampass Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qmw8-x364-xxxm
CVE: CVE-2023-3191
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-06-10
Source: https://github.com/advisories/GHSA-qmw8-x364-xxxm
Type: github-advisory

## Affected
- Packagist: `nilsteampassnet/teampass` — affected >=0 <3.0.9

## Details
In versions of nilsteampassnet/teampass prior to 3.0.9 some user input was not properly sanitized which may have lead to stored cross-site scripting (XSS) vectors in the application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-3191
- https://github.com/nilsteampassnet/teampass/commit/241dbd4159a5d63b55af426464d30dbb53925705
- https://github.com/nilsteampassnet/teampass
- https://huntr.dev/bounties/19fed157-128d-4bfb-a30e-eadf748cbd1a
