# [M] Apache Camel Missing Header Out Filter Leads to Potential Bypass/Injection Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-vq4p-pchp-6g6v
CVE: CVE-2025-30177
CWE: CWE-164
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-04-01
Source: https://github.com/advisories/GHSA-vq4p-pchp-6g6v
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-undertow` — affected >=4.10.0 <4.10.3
- Maven: `org.apache.camel:camel-undertow` — affected >=4.8.0 <4.8.6

## Details
Bypass/Injection vulnerability in Apache Camel in Camel-Undertow component under particular conditions.

This issue affects Apache Camel: from 4.10.0 before 4.10.3, from 4.8.0 before 4.8.6.

Users are recommended to upgrade to version 4.10.3 for 4.10.x LTS and 4.8.6 for 4.8.x LTS.

Camel undertow component is vulnerable to Camel message header injection, in particular the custom header filter strategy used by the component only filter the "out" direction, while it doesn't filter the "in" direction.


This allows an attacker to include Camel specific headers that for some Camel components can alter the behaviour such as the camel-bean component, or the camel-exec component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-30177
- https://github.com/apache/camel/commit/9fd8fc30dbd98511a1faa0cbcf39ef5aeec88a64
- https://camel.apache.org/security/CVE-2025-27636.html
- https://camel.apache.org/security/CVE-2025-29891.html
- https://github.com/apache/camel
- https://lists.apache.org/thread/dj79zdgw01j337lr9gvyy4sv8xfyw8py
