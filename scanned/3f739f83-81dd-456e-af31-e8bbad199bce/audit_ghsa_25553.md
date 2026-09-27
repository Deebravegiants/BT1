# [C] RCE in Studio-42 elFinder on Windows before 2.1.61

## Summary
Severity: Critical
Advisory: GHSA-6p96-vfrc-fv32
CVE: CVE-2022-27115
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-12
Source: https://github.com/advisories/GHSA-6p96-vfrc-fv32
Type: github-advisory

## Affected
- Packagist: `studio-42/elfinder` — affected >=0 <2.1.61

## Details
In Studio-42 elFinder 2.1.60, there is a vulnerability that causes remote code execution through file name bypass for file upload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27115
- https://github.com/Studio-42/elFinder/issues/3458
- https://github.com/Studio-42/elFinder/commit/69be51eea5b484822a29ddd40f1b72845954ba60
