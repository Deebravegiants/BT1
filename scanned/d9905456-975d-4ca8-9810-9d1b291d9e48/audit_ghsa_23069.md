# [C] Pebble Templates Improper Input Validation vulnerability

## Summary
Severity: Critical
Advisory: GHSA-83m8-7hj8-ff5w
CVE: CVE-2019-19899
CWE: CWE-20, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-83m8-7hj8-ff5w
Type: github-advisory

## Affected
- Maven: `io.pebbletemplates:pebble-project` — affected >=0 <3.1.4

## Details
Pebble Templates prior to 3.1.4 allows attackers to bypass a protection mechanism (intended to block access to instances of java.lang.Class) because getClass is accessible via the public static java.lang.Class `java.lang.Class.forName(java.lang.Module,java.lang.String)` signature.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-19899
- https://github.com/PebbleTemplates/pebble/issues/493
- https://github.com/PebbleTemplates/pebble/pull/511
- https://github.com/PebbleTemplates/pebble
- https://research.securitum.com/server-side-template-injection-on-the-example-of-pebble
