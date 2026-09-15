# [M] CVE-2025-67901

## Summary
Severity: Medium
Advisory: CVE-2025-67901
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-14
Source: https://osv.dev/vulnerability/CVE-2025-67901
Type: osv

## Details
openrsync through 0.5.0, as used in OpenBSD through 7.8 and on other platforms, allows a client to cause a server SIGSEGV by specifying a length of zero for block data, because the relationship between p->rem and p->len is not checked.

## References
- https://github.com/openbsd/src/blob/60b9c3dff1abf933e85e3c4d96b54201ee947513/usr.bin/rsync/blocks.c#L480-L481
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/67xxx/CVE-2025-67901.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-67901
- https://github.com/kristapsdz/openrsync/issues/34
