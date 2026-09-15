# [M] CVE-2019-9211

## Summary
Severity: Medium
Advisory: CVE-2019-9211
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-02-27
Source: https://osv.dev/vulnerability/CVE-2019-9211
Type: osv

## Details
There is a reachable assertion abort in the function write_long_string_missing_values() in data/sys-file-writer.c in libdata.a in GNU PSPP 1.2.0 that will lead to denial of service.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/O3QC6VFE2D7M6ZJXBXRIO4JZPKY57CLV/
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00068.html
- http://www.securityfocus.com/bid/107190
- https://bugzilla.redhat.com/show_bug.cgi?id=1683499
