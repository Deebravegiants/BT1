# [H] Gadget chain attack in Nippy

## Summary
Severity: High
Advisory: GHSA-p5gm-fgfx-hr7h
CVE: CVE-2020-24164
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-p5gm-fgfx-hr7h
Type: github-advisory

## Affected
- Maven: `com.taoensso:nippy` — affected >=0 <2.14.2

## Details
A deserialization flaw is present in Taoensso Nippy before 2.14.2. In some circumstances, it is possible for an attacker to create a malicious payload that, when deserialized, will allow arbitrary code to be executed. This occurs because there is automatic use of the Java Serializable interface.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-24164
- https://github.com/ptaoussanis/nippy/issues/130
- https://github.com/ptaoussanis/nippy/commit/61fb009fdde2994140f2da2e495ba8af3a873eb2
