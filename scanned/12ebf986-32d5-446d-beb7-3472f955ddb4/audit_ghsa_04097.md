# [H] Billion laughs attack in c3p0

## Summary
Severity: High
Advisory: GHSA-84p2-vf58-xhxv
CVE: CVE-2019-5427
CWE: CWE-776
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-04-23
Source: https://github.com/advisories/GHSA-84p2-vf58-xhxv
Type: github-advisory

## Affected
- Maven: `com.mchange:c3p0` — affected >=0 <0.9.5.4

## Details
c3p0 version < 0.9.5.4 may be exploited by a billion laughs attack when loading XML configuration due to missing protections against recursive entity expansion when loading configuration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-5427
- https://hackerone.com/reports/509315
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BFIVX6HOVNLAM7W3SUAMHYRNLCVQSAWR
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MQ47OFV57Y2DAHMGA5H3JOL4WHRWRFN4
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
