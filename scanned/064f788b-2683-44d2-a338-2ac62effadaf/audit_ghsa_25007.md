# [H] Improper Verification of Cryptographic Signature in Apache Netbeans

## Summary
Severity: High
Advisory: GHSA-cf8q-j9h3-7237
CVE: CVE-2019-17561
CWE: CWE-20, CWE-347
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-cf8q-j9h3-7237
Type: github-advisory

## Affected
- Maven: `org.codehaus.mevenide:netbeans` — affected >=0

## Details
The "Apache NetBeans" autoupdate system does not fully validate code signatures. An attacker could modify the downloaded nbm and include additional code. "Apache NetBeans" versions up to and including 11.2 are affected by this vulnerability. NetBeans releases before the Apache transition started may also be affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-17561
- https://lists.apache.org/thread.html/rb218aa720fc525f63d91761fbf67854f454ce7a697dbbee2001ae8b1%40%3Cdev.netbeans.apache.org%3E
- https://www.oracle.com/security-alerts/cpujul2020.html
