# [H] RuoYi vulnerable to arbitrary file download

## Summary
Severity: High
Advisory: GHSA-h4c9-rr5m-32fm
CVE: CVE-2023-27025
CWE: CWE-494
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-04-02
Source: https://github.com/advisories/GHSA-h4c9-rr5m-32fm
Type: github-advisory

## Affected
- Maven: `com.ruoyi:ruoyi` — affected >=0 <4.7.7

## Details
An arbitrary file download vulnerability in the background management module of RuoYi v4.7.6 and below allows attackers to download arbitrary files in the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-27025
- https://gitee.com/y_project/RuoYi
- https://gitee.com/y_project/RuoYi/commit/432d5ce1be2e9384a6230d7ccd8401eef5ce02b0
- https://gitee.com/y_project/RuoYi/issues/I697Q5
