# [H] CVE-2020-6077

## Summary
Severity: High
Advisory: CVE-2020-6077
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-03-24
Source: https://osv.dev/vulnerability/CVE-2020-6077
Type: osv

## Details
An exploitable denial-of-service vulnerability exists in the message-parsing functionality of Videolabs libmicrodns 0.1.0. When parsing mDNS messages, the implementation does not properly keep track of the available data in the message, possibly leading to an out-of-bounds read that would result in a denial of service. An attacker can send an mDNS message to trigger this vulnerability.

## References
- https://security.gentoo.org/glsa/202005-10
- https://www.debian.org/security/2020/dsa-4671
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1000
