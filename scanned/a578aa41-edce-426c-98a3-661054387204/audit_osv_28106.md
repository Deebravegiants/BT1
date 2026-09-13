# [H] CVE-2024-27629

## Summary
Severity: High
Advisory: CVE-2024-27629
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-28
Source: https://osv.dev/vulnerability/CVE-2024-27629
Type: osv

## Details
An issue in dc2niix before v.1.0.20240202 allows a local attacker to execute arbitrary code via the generated file name is not properly escaped and injected into a system call when certain types of compression are used.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27629.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27629
- https://github.com/rordenlab/dcm2niix/pull/789
