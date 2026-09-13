# [M] CVE-2021-3448

## Summary
Severity: Medium
Advisory: CVE-2021-3448
CVSS: 4.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:L/A:N)
Published: 2021-04-08
Source: https://osv.dev/vulnerability/CVE-2021-3448
Type: osv

## Details
A flaw was found in dnsmasq in versions before 2.85. When configured to use a specific server for a given network interface, dnsmasq uses a fixed port while forwarding queries. An attacker on the network, able to find the outgoing port used by dnsmasq, only needs to guess the random transmission ID to forge a reply and get it accepted by dnsmasq. This flaw makes a DNS Cache Poisoning attack much easier. The highest threat from this vulnerability is to data integrity.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CVTJUOFFFHINLKWAOC2ZSC5MOPD4SJ24/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FHG7GWSQWKF7JXIMLOGJBKZWBB4VIAJ7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GHURNEHHUBSW45KMIZ4FNBCSUPWPGV5V/
- https://security.gentoo.org/glsa/202105-20
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1939368
