# [M] CVE-2022-4121

## Summary
Severity: Medium
Advisory: CVE-2022-4121
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-01-17
Source: https://osv.dev/vulnerability/CVE-2022-4121
Type: osv

## Details
In libetpan a null pointer dereference in mailimap_mailbox_data_status_free in low-level/imap/mailimap_types.c was found that could lead to a remote denial of service or other potential consequences.

## References
- https://lists.debian.org/debian-lts-announce/2025/07/msg00018.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/4xxx/CVE-2022-4121.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-4121
- https://github.com/dinhvh/libetpan/issues/420
- https://github.com/dinhvh/libetpan/commit/5c9eb6b6ba64c4eb927d7a902317410181aacbba
