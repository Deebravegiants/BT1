# [H] Netplex Json-smart Uncontrolled Recursion vulnerability

## Summary
Severity: High
Advisory: GHSA-pq2g-wx69-c263
CVE: CVE-2024-57699
CWE: CWE-674
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-02-06
Source: https://github.com/advisories/GHSA-pq2g-wx69-c263
Type: github-advisory

## Affected
- Maven: `net.minidev:json-smart` — affected >=2.5.0 <2.5.2

## Details
A security issue was found in Netplex Json-smart 2.5.0 through 2.5.1. When loading a specially crafted JSON input, containing a large number of ’{’, a stack exhaustion can be trigger, which could allow an attacker to cause a Denial of Service (DoS). This issue exists because of an incomplete fix for CVE-2023-1370.

The fixed version only addresses the default modes provided by [JSONParser](https://github.com/netplex/json-smart-v2/blob/master/json-smart/src/main/java/net/minidev/json/parser/JSONParser.java#L118), such as `MODE_RFC4627`. If you create the JSONParser manually or with custom options, make sure to set the `LIMIT_JSON_DEPTH` option.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-57699
- https://github.com/netplex/json-smart-v2/issues/232
- https://github.com/netplex/json-smart-v2/issues/233
- https://github.com/netplex/json-smart-v2/issues/236
- https://github.com/TurtleLiu/Vul_PoC/tree/main/CVE-2024-57699
- https://github.com/netplex/json-smart-v2
- https://github.com/netplex/json-smart-v2/releases/tag/2.5.2
- https://nvd.nist.gov/vuln/detail/cve-2023-1370
