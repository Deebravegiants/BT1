# [H] CVE-2017-7401

## Summary
Severity: High
Advisory: CVE-2017-7401
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-03
Source: https://osv.dev/vulnerability/CVE-2017-7401
Type: osv

## Details
Incorrect interaction of the parse_packet() and parse_part_sign_sha256() functions in network.c in collectd 5.7.1 and earlier allows remote attackers to cause a denial of service (infinite loop) of a collectd instance (configured with "SecurityLevel None" and with empty "AuthFile" options) via a crafted UDP packet.

## References
- http://www.securityfocus.com/bid/97321
- https://access.redhat.com/errata/RHSA-2017:1285
- https://access.redhat.com/errata/RHSA-2017:1787
- https://access.redhat.com/errata/RHSA-2018:2615
- https://github.com/collectd/collectd/issues/2174
