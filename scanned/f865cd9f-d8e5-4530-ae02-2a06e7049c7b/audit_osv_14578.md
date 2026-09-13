# [H] CVE-2019-10162

## Summary
Severity: High
Advisory: CVE-2019-10162
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-07-30
Source: https://osv.dev/vulnerability/CVE-2019-10162
Type: osv

## Details
A vulnerability has been found in PowerDNS Authoritative Server before versions 4.1.10, 4.0.8 allowing an authorized user to cause the server to exit by inserting a crafted record in a MASTER type zone under their control. The issue is due to the fact that the Authoritative Server will exit when it runs into a parsing error while looking up the NS/A/AAAA records it is about to use for an outgoing notify.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00036.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00054.html
- https://blog.powerdns.com/2019/06/21/powerdns-authoritative-server-4-0-8-and-4-1-10-released/
- https://doc.powerdns.com/authoritative/security-advisories/powerdns-advisory-2019-04.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10162
