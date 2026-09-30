# [H] Use of Hard-coded Credentials in Nacos

## Summary
Severity: High
Advisory: GHSA-2g86-r6w2-wqqr
CVE: CVE-2021-43116
CWE: CWE-287, CWE-798
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-06
Source: https://github.com/advisories/GHSA-2g86-r6w2-wqqr
Type: github-advisory

## Affected
- Maven: `com.alibaba.nacos:nacos-client` — affected >=0

## Details
An Access Control vulnerability exists in Nacos 2.0.3 in the access prompt page; enter username and password, click on login to capture packets and then change the returned package, which lets a malicious user login.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-43116
- https://github.com/alibaba/nacos/issues/7127
- https://github.com/alibaba/nacos/issues/7182
- https://github.com/alibaba/nacos
- http://packetstormsecurity.com/files/171638/Nacos-2.0.3-Access-Control.html
