# [H] Improper Neutralization of Directives in Dynamically Evaluated Code in Spring Framework

## Summary
Severity: High
Advisory: GHSA-wv88-pf73-x22p
CVE: CVE-2011-2730
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-wv88-pf73-x22p
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-core` — affected >=3.0.0 <3.0.6
- Maven: `org.springframework:spring-core` — affected >=0 <2.5.6.SEC03
- Maven: `org.springframework:spring-core` — affected >=2.5.7.SR0 <2.5.7.SR023

## Details
VMware SpringSource Spring Framework before 2.5.6.SEC03, 2.5.7.SR023, and 3.x before 3.0.6, when a container supports Expression Language (EL), evaluates EL expressions in tags twice, which allows remote attackers to obtain sensitive information via a (1) name attribute in a (a) spring:hasBindErrors tag; (2) path attribute in a (b) spring:bind or (c) spring:nestedpath tag; (3) arguments, (4) code, (5) text, (6) var, (7) scope, or (8) message attribute in a (d) spring:message or (e) spring:theme tag; or (9) var, (10) scope, or (11) value attribute in a (f) spring:transform tag, aka "Expression Language Injection."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-2730
- https://github.com/spring-projects/spring-framework/commit/62ccc8dd7e645fb91705d44919abac838cb5ca3f
- https://github.com/spring-projects/spring-framework/commit/9772eb8410e37cd0bdec0d1b133218446c778beb
- https://github.com/spring-projects/spring-framework/commit/b8d86330d1fadc645630416c3aaebf131bf749fc
- https://docs.google.com/document/d/1dc1xxO8UMFaGLOwgkykYdghGWm_2Gn0iCrxFsympqcE/edit
- https://github.com/spring-projects/spring-framework
- http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=677814
- http://rhn.redhat.com/errata/RHSA-2013-0191.html
- http://rhn.redhat.com/errata/RHSA-2013-0192.html
- http://rhn.redhat.com/errata/RHSA-2013-0194.html
- http://rhn.redhat.com/errata/RHSA-2013-0195.html
- http://rhn.redhat.com/errata/RHSA-2013-0196.html
- http://rhn.redhat.com/errata/RHSA-2013-0198.html
- http://rhn.redhat.com/errata/RHSA-2013-0221.html
- http://rhn.redhat.com/errata/RHSA-2013-0533.html
- http://www.debian.org/security/2012/dsa-2504
- http://www.oracle.com/technetwork/security-advisory/cpujul2017-3236622.html
