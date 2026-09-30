# [H] Insecure serialization leading to RCE in serialize-javascript

## Summary
Severity: High
Advisory: GHSA-hxcc-f52p-wc94
CVE: CVE-2020-7660
CWE: CWE-502
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-08-11
Source: https://github.com/advisories/GHSA-hxcc-f52p-wc94
Type: github-advisory

## Affected
- npm: `serialize-javascript` — affected >=0 <3.1.0

## Details
serialize-javascript prior to 3.1.0 allows remote attackers to inject arbitrary code via the function "deleteFunctions" within "index.js". 

An object such as `{"foo": /1"/, "bar": "a\"@__R-<UID>-0__@"}` was serialized as `{"foo": /1"/, "bar": "a\/1"/}`, which allows an attacker to escape the `bar` key. This requires the attacker to control the values of both `foo` and `bar` and guess the value of `<UID>`. The UID has a keyspace of approximately 4 billion making it a realistic network attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7660
- https://github.com/yahoo/serialize-javascript/commit/f21a6fb3ace2353413761e79717b2d210ba6ccbd
- https://github.com/yahoo/serialize-javascript
