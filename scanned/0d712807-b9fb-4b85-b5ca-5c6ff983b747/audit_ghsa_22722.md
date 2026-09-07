# [C] Arbitrary code execution in Richfaces

## Summary
Severity: Critical
Advisory: GHSA-4j38-wjhf-884r
CVE: CVE-2018-12533
CWE: CWE-917
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-4j38-wjhf-884r
Type: github-advisory

## Affected
- Maven: `org.richfaces:richfaces-core` — affected >=3.1.0

## Details
JBoss RichFaces 3.1.0 through 3.3.4 allows unauthenticated remote attackers to inject expression language (EL) expressions and execute arbitrary Java code via a /DATA/ substring in a path with an org.richfaces.renderkit.html.Paint2DResource$ImageData object, aka RF-14310.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-12533
- https://access.redhat.com/errata/RHSA-2018:2663
- https://access.redhat.com/errata/RHSA-2018:2664
- https://access.redhat.com/errata/RHSA-2018:2930
- https://codewhitesec.blogspot.com/2018/05/poor-richfaces.html
- http://seclists.org/fulldisclosure/2020/Mar/21
