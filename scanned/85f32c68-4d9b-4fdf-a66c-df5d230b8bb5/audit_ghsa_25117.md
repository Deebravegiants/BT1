# [M] Singularity Incorrect Access Control 

## Summary
Severity: Medium
Advisory: GHSA-4x32-h296-rg6j
CVE: CVE-2018-12021
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-4x32-h296-rg6j
Type: github-advisory

## Affected
- Go: `github.com/hpcng/singularity` — affected >=2.3.0 <2.5.2

## Details
Singularity 2.3.0 through 2.5.1 is affected by an incorrect access control on systems supporting overlay file system. When using the overlay option, a malicious user may access sensitive information by exploiting a few specific Singularity features.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-12021
- https://github.com/singularityware/singularity
- https://github.com/singularityware/singularity/releases/tag/2.5.2
- http://www.openwall.com/lists/oss-security/2019/05/16/1
