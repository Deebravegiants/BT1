# [H] Insertion of Sensitive Information Into Debugging Code in Microweber

## Summary
Severity: High
Advisory: GHSA-mjvc-j6rv-9xj8
CVE: CVE-2022-0721
CWE: CWE-215
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-24
Source: https://github.com/advisories/GHSA-mjvc-j6rv-9xj8
Type: github-advisory

## Affected
- Packagist: `microweber/microweber` — affected >=0 <1.3

## Details
Microweber prior to 1.3 may expose sensitive information about a server and a user when running the server in debug mode.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0721
- https://github.com/microweber/microweber/commit/b12e1a490c79460bff019f34b2e17112249b16ec
- https://github.com/microweber/microweber
- https://huntr.dev/bounties/ae267d39-9750-4c69-be8b-4f915da089fb
