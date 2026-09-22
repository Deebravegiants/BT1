# [H] CVE-2020-6078

## Summary
Severity: High
Advisory: CVE-2020-6078
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-03-24
Source: https://osv.dev/vulnerability/CVE-2020-6078
Type: osv

## Details
An exploitable denial-of-service vulnerability exists in the message-parsing functionality of Videolabs libmicrodns 0.1.0. When parsing mDNS messages in mdns_recv, the return value of the mdns_read_header function is not checked, leading to an uninitialized variable usage that eventually results in a null pointer dereference, leading to service crash. An attacker can send a series of mDNS messages to trigger this vulnerability.

## References
- https://security.gentoo.org/glsa/202005-10
- https://www.debian.org/security/2020/dsa-4671
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1001
