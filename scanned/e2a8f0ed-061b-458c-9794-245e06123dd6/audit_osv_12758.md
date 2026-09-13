# [H] CVE-2018-14645

## Summary
Severity: High
Advisory: CVE-2018-14645
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-09-21
Source: https://osv.dev/vulnerability/CVE-2018-14645
Type: osv

## Details
A flaw was discovered in the HPACK decoder of HAProxy, before 1.8.14, that is used for HTTP/2. An out-of-bounds read access in hpack_valid_idx() resulted in a remote crash and denial of service.

## References
- https://www.mail-archive.com/haproxy%40formilux.org/msg31253.html
- https://access.redhat.com/errata/RHBA-2019:0028
- https://access.redhat.com/errata/RHSA-2018:2882
- https://usn.ubuntu.com/3780-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14645
