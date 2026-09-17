# [M] CVE-2019-10163

## Summary
Severity: Medium
Advisory: CVE-2019-10163
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2019-07-30
Source: https://osv.dev/vulnerability/CVE-2019-10163
Type: osv

## Details
A Vulnerability has been found in PowerDNS Authoritative Server before versions 4.1.9, 4.0.8 allowing a remote, authorized master server to cause a high CPU load or even prevent any further updates to any slave zone by sending a large number of NOTIFY messages. Note that only servers configured as slaves are affected by this issue.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00036.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00054.html
- https://blog.powerdns.com/2019/06/21/powerdns-authoritative-server-4-0-8-and-4-1-10-released/
- https://doc.powerdns.com/authoritative/security-advisories/powerdns-advisory-2019-05.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10163
