# [M] CVE-2017-3143

## Summary
Severity: Medium
Advisory: CVE-2017-3143
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/CVE-2017-3143
Type: osv

## Details
An attacker who is able to send and receive messages to an authoritative DNS server and who has knowledge of a valid TSIG key name for the zone and service being targeted may be able to manipulate BIND into accepting an unauthorized dynamic update. Affects BIND 9.4.0->9.8.8, 9.9.0->9.9.10-P1, 9.10.0->9.10.5-P1, 9.11.0->9.11.1-P1, 9.9.3-S1->9.9.10-S2, 9.10.5-S1->9.10.5-S2.

## References
- http://www.securityfocus.com/bid/99337
- http://www.securitytracker.com/id/1038809
- https://access.redhat.com/errata/RHSA-2017:1679
- https://access.redhat.com/errata/RHSA-2017:1680
- https://h20566.www2.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbux03772en_us
- https://kb.isc.org/docs/aa-01503
- https://security.netapp.com/advisory/ntap-20190830-0003/
- https://www.debian.org/security/2017/dsa-3904
