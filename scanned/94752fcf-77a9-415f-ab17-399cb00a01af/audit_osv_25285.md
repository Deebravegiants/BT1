# [M] A NULL pointer dereference in TIFFClose() is caused by a failure to open an output file (non-existent path or a path that requires permissions like /dev/null) while specifying zones.

## Summary
Severity: Medium
Advisory: CVE-2023-3316
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-06-19
Source: https://osv.dev/vulnerability/CVE-2023-3316
Type: osv

## Details
A NULL pointer dereference in TIFFClose() is caused by a failure to open an output file (non-existent path or a path that requires permissions like /dev/null) while specifying zones.

## References
- https://lists.debian.org/debian-lts-announce/2023/07/msg00034.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00019.html
- https://research.jfrog.com/vulnerabilities/libtiff-nullderef-dos-xray-522144/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3316.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3316
- https://gitlab.com/libtiff/libtiff/-/issues/515
- https://gitlab.com/libtiff/libtiff/-/merge_requests/468
