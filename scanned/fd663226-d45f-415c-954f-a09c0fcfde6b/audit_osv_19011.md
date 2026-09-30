# [H] CVE-2020-6071

## Summary
Severity: High
Advisory: CVE-2020-6071
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-03-24
Source: https://osv.dev/vulnerability/CVE-2020-6071
Type: osv

## Details
An exploitable denial-of-service vulnerability exists in the resource record-parsing functionality of Videolabs libmicrodns 0.1.0. When parsing compressed labels in mDNS messages, the compression pointer is followed without checking for recursion, leading to a denial of service. An attacker can send an mDNS message to trigger this vulnerability.

## References
- https://security.gentoo.org/glsa/202005-10
- https://www.debian.org/security/2020/dsa-4671
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-0994
