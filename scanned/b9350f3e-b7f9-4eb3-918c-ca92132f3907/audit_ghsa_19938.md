# [M] hutool-json stack overflow vulnerability

## Summary
Severity: Medium
Advisory: GHSA-whgh-g24c-3j5q
CVE: CVE-2022-45690
Ecosystem: Maven
Published: 2022-12-13
Source: https://github.com/advisories/GHSA-whgh-g24c-3j5q
Type: github-advisory

## Affected
- Maven: `cn.hutool:hutool-json` — affected >=0 <5.8.11

## Details
A stack overflow in the org.json.JSONTokener.nextValue::JSONTokener.java component of hutool-json v5.8.10 allows attackers to cause a Denial of Service (DoS) via crafted JSON or XML data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45690
- https://github.com/dromara/hutool/issues/2746
- https://github.com/stleary/JSON-java/issues/654
- https://github.com/stleary/JSON-java/commit/7a124d857dc8da1165c87fa788e53359a317d0f7
- https://github.com/dromara/hutool
