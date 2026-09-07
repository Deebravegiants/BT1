# [M] Beetl's SpELFunction extension function has an expression injection risk

## Summary
Severity: Medium
Advisory: GHSA-fmmw-44rp-jcfp
CVE: CVE-2026-8759
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-17
Source: https://github.com/advisories/GHSA-fmmw-44rp-jcfp
Type: github-advisory

## Affected
- Maven: `com.ibeetl:beetl-spring-classic` — affected >=0

## Details
A vulnerability was identified in xiandafu beetl up to 3.20.2. Affected is an unknown function of the file beetl-classic-integration/beetl-spring-classic/src/main/java/org/beetl/ext/spring/SpELFunction.java of the component SpELFunction. The manipulation leads to improper neutralization of special elements used in an expression language statement. Remote exploitation of the attack is possible. The exploit is publicly available and might be used. The project was informed of the problem early through an issue report but has not responded yet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-8759
- https://gitee.com/xiandafu/beetl
- https://gitee.com/xiandafu/beetl/issues/IIYAWC
- https://vuldb.com/submit/811316
- https://vuldb.com/vuln/364386
- https://vuldb.com/vuln/364386/cti
