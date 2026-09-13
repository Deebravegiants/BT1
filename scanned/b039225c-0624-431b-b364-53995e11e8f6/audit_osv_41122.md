# [H] CVE-2026-57918

## Summary
Severity: High
Advisory: CVE-2026-57918
CVSS: 7.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:L)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-57918
Type: osv

## Details
libnfs through 6.0.2 before 935b8db has an xid integer underflow in READ_IOVEC in rpc_read_from_socket in lib/socket.c during a connection to a crafted NFS server, when the expected pdu size exceeds the absolute pdu size from the xid/record-marker.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57918.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-57918
- https://github.com/sahlberg/libnfs/commit/935b8db712b3c6649bc57ddc276526c4a31680de
