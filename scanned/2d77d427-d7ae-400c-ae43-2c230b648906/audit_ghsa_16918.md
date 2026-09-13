# [M] Code injection in Apache Zeppelin Shell

## Summary
Severity: Medium
Advisory: GHSA-8pfj-w89w-m24x
CVE: CVE-2024-31861
CWE: CWE-94
Ecosystem: Maven
Published: 2024-04-11
Source: https://github.com/advisories/GHSA-8pfj-w89w-m24x
Type: github-advisory

## Affected
- Maven: `org.apache.zeppelin:zeppelin-shell` — affected >=0.10.1 <0.11.1

## Details
Improper Control of Generation of Code ('Code Injection') vulnerability in Apache Zeppelin.

The attackers can use Shell interpreter as a code generation gateway, and execute the generated code as a normal way.
This issue affects Apache Zeppelin: from 0.10.1 before 0.11.1.

Users are recommended to upgrade to version 0.11.1, which doesn't have Shell interpreter by default.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-31861
- https://github.com/apache/zeppelin/pull/4708
- https://github.com/apache/zeppelin
- https://lists.apache.org/thread/99clvqrht5l5r6kzjzwg2kj94boc9sfh
- http://www.openwall.com/lists/oss-security/2024/04/10/8
