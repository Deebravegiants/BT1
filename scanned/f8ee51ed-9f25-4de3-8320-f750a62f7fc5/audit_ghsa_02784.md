# [C] Prototype pollution vulnerability in 'libnested'

## Summary
Severity: Critical
Advisory: GHSA-3r9x-mjrm-2725
CVE: CVE-2020-28283
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-3r9x-mjrm-2725
Type: github-advisory

## Affected
- npm: `libnested` — affected >=0.0.0

## Details
Prototype pollution vulnerability in 'libnested' versions 0.0.0 through 1.5.0 allows an attacker to cause a denial of service and may lead to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28283
- https://github.com/dominictarr/libnested
- https://github.com/dominictarr/libnested/blob/d028a1b0f2e5f16fc28e568f52b936ae0bca0647/index.js#L27
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2020-28284
