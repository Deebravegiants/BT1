# [C] CVE-2020-6072

## Summary
Severity: Critical
Advisory: CVE-2020-6072
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-24
Source: https://osv.dev/vulnerability/CVE-2020-6072
Type: osv

## Details
An exploitable code execution vulnerability exists in the label-parsing functionality of Videolabs libmicrodns 0.1.0. When parsing compressed labels in mDNS messages, the rr_decode function's return value is not checked, leading to a double free that could be exploited to execute arbitrary code. An attacker can send an mDNS message to trigger this vulnerability.

## References
- https://security.gentoo.org/glsa/202005-10
- https://www.debian.org/security/2020/dsa-4671
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-0995
