# [H] CVE-2021-32739

## Summary
Severity: High
Advisory: CVE-2021-32739
Aliases: GHSA-98wp-jc6q-x5q5
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-07-15
Source: https://osv.dev/vulnerability/CVE-2021-32739
Type: osv

## Details
Icinga is a monitoring system which checks the availability of network resources, notifies users of outages, and generates performance data for reporting. From version 2.4.0 through version 2.12.4, a vulnerability exists that may allow privilege escalation for authenticated API users. With a read-ony user's credentials, an attacker can view most attributes of all config objects including `ticket_salt` of `ApiListener`. This salt is enough to compute a ticket for every possible common name (CN). A ticket, the master node's certificate, and a self-signed certificate are enough to successfully request the desired certificate from Icinga. That certificate may in turn be used to steal an endpoint or API user's identity. Versions 2.12.5 and 2.11.10 both contain a fix the vulnerability. As a workaround, one may either specify queryable types explicitly or filter out ApiListener objects.

## References
- https://lists.debian.org/debian-lts-announce/2024/11/msg00010.html
- https://icinga.com/blog/2021/07/02/releasing-icinga-2-12-5-2-11-10/
- https://lists.debian.org/debian-lts-announce/2021/11/msg00010.html
- https://github.com/Icinga/icinga2/security/advisories/GHSA-98wp-jc6q-x5q5
