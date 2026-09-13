# [H] CVE-2024-43688

## Summary
Severity: High
Advisory: CVE-2024-43688
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-08-20
Source: https://osv.dev/vulnerability/CVE-2024-43688
Type: osv

## Details
cron/entry.c in vixie cron before 9cc8ab1, as used in OpenBSD 7.4 and 7.5, allows a heap-based buffer underflow and memory corruption. NOTE: this issue was introduced during a May 2023 refactoring.

## References
- https://www.supernetworks.org/CVE-2024-43688/openbsd-cron-heap-underflow.txt
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43688.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-43688
- https://www.supernetworks.org/advisories/CVE-2024-43688-openbsd-cron-heap-underflow.txt
- https://github.com/vixie/cron/commit/9cc8ab1087bb9ab861dd5595c41200683c9f6712
