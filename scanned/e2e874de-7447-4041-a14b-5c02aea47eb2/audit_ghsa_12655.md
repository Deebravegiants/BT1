# [C] Apache Accumulo Improper Authentication vulnerability

## Summary
Severity: Critical
Advisory: GHSA-hp5w-w29m-vg63
CVE: CVE-2023-34340
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-21
Source: https://github.com/advisories/GHSA-hp5w-w29m-vg63
Type: github-advisory

## Affected
- Maven: `org.apache.accumulo:accumulo-shell` — affected >=2.1.0 <2.1.1

## Details
Improper Authentication vulnerability in Apache Software Foundation Apache Accumulo.
This issue affects Apache Accumulo: 2.1.0.

Accumulo 2.1.0 contains a defect in the user authentication process that may succeed when invalid credentials are provided. Users are advised to upgrade to 2.1.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-34340
- https://github.com/apache/accumulo/issues/3427
- https://github.com/apache/accumulo/issues/3433
- https://github.com/apache/accumulo/pull/3440
- https://github.com/apache/accumulo/commit/0f2389735fd32e0bbc93ecde5d8c814b275b21b5
- https://accumulo.apache.org/release/accumulo-2.1.1
- https://github.com/apache/accumulo
- https://lists.apache.org/thread/syy6jftvy9l6tlhn33o0rzwhh4rd0z4t
