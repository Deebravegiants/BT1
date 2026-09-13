# [M] CVE-2016-6172

## Summary
Severity: Medium
Advisory: CVE-2016-6172
CVSS: 6.8 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-09-26
Source: https://osv.dev/vulnerability/CVE-2016-6172
Type: osv

## Details
PowerDNS (aka pdns) Authoritative Server before 4.0.1 allows remote primary DNS servers to cause a denial of service (memory exhaustion and secondary DNS server crash) via a large (1) AXFR or (2) IXFR response.

## References
- http://www.securityfocus.com/bid/91678
- http://www.securitytracker.com/id/1036242
- http://lists.opensuse.org/opensuse-updates/2016-08/msg00085.html
- http://www.debian.org/security/2016/dsa-3664
- https://doc.powerdns.com/md/changelog/#powerdns-authoritative-server-401
- https://lists.dns-oarc.net/pipermail/dns-operations/2016-July/015058.html
- https://github.com/PowerDNS/pdns/issues/4128
- https://github.com/PowerDNS/pdns/issues/4133
- https://github.com/PowerDNS/pdns/pull/4134
- https://github.com/sischkg/xfer-limit/blob/master/README.md
- http://www.openwall.com/lists/oss-security/2016/07/06/3
