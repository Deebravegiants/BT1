# [H] CVE-2018-20615

## Summary
Severity: High
Advisory: CVE-2018-20615
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-03-21
Source: https://osv.dev/vulnerability/CVE-2018-20615
Type: osv

## Details
An out-of-bounds read issue was discovered in the HTTP/2 protocol decoder in HAProxy 1.8.x and 1.9.x through 1.9.0 which can result in a crash. The processing of the PRIORITY flag in a HEADERS frame requires 5 extra bytes, and while these bytes are skipped, the total frame length was not re-checked to make sure they were present in the frame.

## References
- https://www.mail-archive.com/haproxy%40formilux.org/msg32304.html
- http://lists.opensuse.org/opensuse-security-announce/2019-02/msg00018.html
- http://www.securityfocus.com/bid/106645
- https://access.redhat.com/errata/RHBA-2019:0327
- https://access.redhat.com/errata/RHSA-2019:0275
- https://usn.ubuntu.com/3858-1/
