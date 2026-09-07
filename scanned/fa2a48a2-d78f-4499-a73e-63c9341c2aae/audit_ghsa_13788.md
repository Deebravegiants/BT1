# [H] Dromara Lamp-Cloud Use of Hard-coded Cryptographic Key

## Summary
Severity: High
Advisory: GHSA-xr8c-mq5x-5f56
CVE: CVE-2023-31579
CWE: CWE-798
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-11-03
Source: https://github.com/advisories/GHSA-xr8c-mq5x-5f56
Type: github-advisory

## Affected
- Maven: `top.tangyh.basic:lamp-core` — affected >=0 <3.8.1
- Maven: `top.tangyh.basic:lamp-util` — affected >=0 <3.8.1

## Details
Dromara Lamp-Cloud before v3.8.1 was discovered to use a hardcoded cryptographic key when creating and verifying a Json Web Token. This vulnerability allows attackers to authenticate to the application via a crafted JWT token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-31579
- https://github.com/dromara/lamp-cloud/issues/183
- https://github.com/dromara/lamp-cloud/commit/31f79b122d85ed1b4f354673212692aa8205437a
- https://github.com/xubowenW/JWTissues/blob/main/lamp%20issue.md
