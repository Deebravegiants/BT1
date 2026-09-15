# [M] cJSON cJSON_Compare Exponential Complexity Denial of Service

## Summary
Severity: Medium
Advisory: CVE-2026-67216
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/CVE-2026-67216
Type: osv

## Details
cJSON through 1.7.19 contains an inefficient algorithmic complexity flaw in cJSON_Compare(). When comparing objects, the function recurses into each shared subtree twice, once in each direction, with no depth guard, making the running time exponential in nesting depth. A small, deeply nested document of a few hundred bytes (depth around 40) compared for equality consumes hours of CPU, and the cost roughly doubles with each additional level of nesting. An application that calls cJSON_Compare() on attacker-influenced JSON that is structurally equal to a reference document is exposed to a denial-of-service condition.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67216.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-67216
- https://www.vulncheck.com/advisories/cjson-cjson-compare-exponential-complexity-denial-of-service
- https://github.com/DaveGamble/cJSON/blob/v1.7.19/cJSON.c#L3057-L3180
- https://joshua.hu/cjson-json-parser-cve-vulnerabilities
