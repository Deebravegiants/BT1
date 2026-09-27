# [H] CVE-2019-12494

## Summary
Severity: High
Advisory: CVE-2019-12494
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-06-05
Source: https://osv.dev/vulnerability/CVE-2019-12494
Type: osv

## Details
In Gardener before 0.20.0, incorrect access control in seed clusters allows information disclosure by sending HTTP GET requests from one's own shoot clusters to foreign shoot clusters. This occurs because traffic from shoot to seed via the VPN endpoint is not blocked.

## References
- https://groups.google.com/forum/#%21topic/gardener/pH6dNIEhv-A
- https://github.com/gardener/vpn/issues/40
- https://github.com/gardener/gardener/pull/874
