# [H] CVE-2020-6073

## Summary
Severity: High
Advisory: CVE-2020-6073
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-03-24
Source: https://osv.dev/vulnerability/CVE-2020-6073
Type: osv

## Details
An exploitable denial-of-service vulnerability exists in the TXT record-parsing functionality of Videolabs libmicrodns 0.1.0. When parsing the RDATA section in a TXT record in mDNS messages, multiple integer overflows can be triggered, leading to a denial of service. An attacker can send an mDNS message to trigger this vulnerability.

## References
- https://security.gentoo.org/glsa/202005-10
- https://www.debian.org/security/2020/dsa-4671
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-0996
