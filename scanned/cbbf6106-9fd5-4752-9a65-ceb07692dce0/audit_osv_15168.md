# [H] CVE-2019-14241

## Summary
Severity: High
Advisory: CVE-2019-14241
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-07-23
Source: https://osv.dev/vulnerability/CVE-2019-14241
Type: osv

## Details
HAProxy through 2.0.2 allows attackers to cause a denial of service (ha_panic) via vectors related to htx_manage_client_side_cookies in proto_htx.c.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00060.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00062.html
- http://www.securityfocus.com/bid/109352
- https://github.com/haproxy/haproxy/issues/181
