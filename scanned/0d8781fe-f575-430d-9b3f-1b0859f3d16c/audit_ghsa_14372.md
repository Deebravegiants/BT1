# [H] json-smart Uncontrolled Recursion vulnerability

## Summary
Severity: High
Advisory: GHSA-493p-pfq6-5258
CVE: CVE-2023-1370
CWE: CWE-674
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-23
Source: https://github.com/advisories/GHSA-493p-pfq6-5258
Type: github-advisory

## Affected
- Maven: `net.minidev:json-smart` — affected >=0 <2.4.9

## Details
### Impact
Affected versions of [net.minidev:json-smart](https://github.com/netplex/json-smart-v1) are vulnerable to Denial of Service (DoS) due to a StackOverflowError when parsing a deeply nested JSON array or object.

When reaching a ‘[‘ or ‘{‘ character in the JSON input, the code parses an array or an object respectively. It was discovered that the 3PP does not have any limit to the nesting of such arrays or objects. Since the parsing of nested arrays and objects is done recursively, nesting too many of them can cause stack exhaustion (stack overflow) and crash the software.

### Patches
This vulnerability was fixed in json-smart version 2.4.9, but the maintainer recommends upgrading to 2.4.10, due to a remaining bug.

### Workarounds
N/A

### References
- https://www.cve.org/CVERecord?id=CVE-2023-1370
- https://nvd.nist.gov/vuln/detail/CVE-2023-1370
- https://security.snyk.io/vuln/SNYK-JAVA-NETMINIDEV-3369748

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1370
- https://github.com/netplex/json-smart-v2/issues/137
- https://github.com/netplex/json-smart-v2/commit/5b3205d051952d3100aa0db1535f6ba6226bd87a
- https://github.com/netplex/json-smart-v2/commit/e2791ae506a57491bc856b439d706c81e45adcf8
- https://github.com/oswaldobapvicjr/jsonmerge
- https://research.jfrog.com/vulnerabilities/stack-exhaustion-in-json-smart-leads-to-denial-of-service-when-parsing-malformed-json-xray-427633
- https://security.netapp.com/advisory/ntap-20240621-0006
- https://security.snyk.io/vuln/SNYK-JAVA-NETMINIDEV-3369748
- https://www.cve.org/CVERecord?id=CVE-2023-1370
