# [M] RuoYi 4.7.3 vulnerable to arbitrary file upload in background management module

## Summary
Severity: Medium
Advisory: GHSA-6w2f-6wq3-rjvf
CVE: CVE-2022-32065
CWE: CWE-434, CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-07-14
Source: https://github.com/advisories/GHSA-6w2f-6wq3-rjvf
Type: github-advisory

## Affected
- Maven: `com.ruoyi:ruoyi` — affected >=0 <4.7.4

## Details
An arbitrary file upload vulnerability in the background management module of RuoYi v4.7.3 and below allows attackers to execute arbitrary code via a crafted HTML file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-32065
- https://github.com/yangzongzhuan/RuoYi/issues/118
- https://github.com/yangzongzhuan/RuoYi/commit/d8b2a9a905fb750fa60e2400238cf4750a77c5e6
- https://gitee.com/y_project/RuoYi/commit/d8b2a9a905fb750fa60e2400238cf4750a77c5e6
- https://gitee.com/y_project/RuoYi/issues/I57IME
- https://github.com/yangzongzhuan/RuoYi
