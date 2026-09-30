# [H] Prototype pollution in dojo

## Summary
Severity: High
Advisory: GHSA-jxfh-8wgv-vfr2
CVE: CVE-2020-5258
CWE: CWE-1321, CWE-74, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2020-03-10
Source: https://github.com/advisories/GHSA-jxfh-8wgv-vfr2
Type: github-advisory

## Affected
- npm: `dojo` — affected >=0 <1.11.10
- npm: `dojo` — affected >=1.12.0 <1.12.8
- npm: `dojo` — affected >=1.13.0 <1.13.7
- npm: `dojo` — affected >=1.14.0 <1.14.6
- npm: `dojo` — affected >=1.15.0 <1.15.3
- npm: `dojo` — affected >=1.16.0 <1.16.2

## Details
In affected versions of dojo (NPM package), the deepCopy method is vulnerable to Prototype Pollution.

Prototype Pollution refers to the ability to inject properties into existing JavaScript language construct prototypes, such as objects.
An attacker manipulates these attributes to overwrite, or pollute, a JavaScript application object prototype of the base object by injecting other values. 

This has been patched in versions 1.12.8, 1.13.7, 1.14.6, 1.15.3 and 1.16.2

## References
- https://github.com/dojo/dojo/security/advisories/GHSA-jxfh-8wgv-vfr2
- https://nvd.nist.gov/vuln/detail/CVE-2020-5258
- https://github.com/dojo/dojo/commit/20a00afb68f5587946dc76fbeaa68c39bda2171d
- https://github.com/dojo/dojo
- https://lists.apache.org/thread.html/r3638722360d7ae95f874280518b8d987d799a76df7a9cd78eac33a1b@%3Cusers.qpid.apache.org%3E
- https://lists.apache.org/thread.html/r665fcc152bd0fec9f71511a6c2435ff24d3a71386b01b1a6df326fd3@%3Cusers.qpid.apache.org%3E
- https://lists.apache.org/thread.html/rf481b3f25f05c52ba4e24991a941c1a6e88d281c6c9360a806554d00@%3Cusers.qpid.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2020/03/msg00012.html
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
