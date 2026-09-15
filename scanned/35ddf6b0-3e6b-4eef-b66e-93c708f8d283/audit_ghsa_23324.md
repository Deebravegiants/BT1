# [H] Singularity insecure permissions

## Summary
Severity: High
Advisory: GHSA-mj73-5x75-9phh
CVE: CVE-2019-19724
CWE: CWE-276
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-mj73-5x75-9phh
Type: github-advisory

## Affected
- Go: `github.com/sylabs/singularity` — affected >=3.3.0 <3.5.2

## Details
Insecure permissions (777) are set on `$HOME/.singularity` when it is newly created by Singularity (version from 3.3.0 to 3.5.1), which could lead to an information leak, and malicious redirection of operations performed against Sylabs cloud services.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-19724
- https://github.com/sylabs/singularity/commit/2cda4981812c29f0fb11d3ea6aaf6139f665a631
- https://github.com/sylabs/singularity
- https://github.com/sylabs/singularity/releases/tag/v3.5.2
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00025.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00059.html
