# [H] CVE-2024-43700

## Summary
Severity: High
Advisory: CVE-2024-43700
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-08-29
Source: https://osv.dev/vulnerability/CVE-2024-43700
Type: osv

## Details
xfpt versions prior to 1.01 fails to handle appropriately some parameters inside the input data, resulting in a stack-based buffer overflow vulnerability. When a user of the affected product is tricked to process a specially crafted file, arbitrary code may be executed on the user's environment.

## References
- https://jvn.jp/en/vu/JVNVU96498690/
- https://lists.debian.org/debian-lts-announce/2024/11/msg00034.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43700.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-43700
- https://github.com/PhilipHazel/xfpt/commit/a690304bbd3fd19e9dfdad50dcc87ad829f744e4
- https://github.com/PhilipHazel/xfpt
