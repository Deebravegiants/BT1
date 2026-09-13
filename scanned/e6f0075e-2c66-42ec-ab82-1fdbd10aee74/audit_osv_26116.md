# [C] HertzBeat AviatorScript Inject RCE

## Summary
Severity: Critical
Advisory: CVE-2023-51388
Aliases: GHSA-mcqg-gqxr-hqgj
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-22
Source: https://osv.dev/vulnerability/CVE-2023-51388
Type: osv

## Details
Hertzbeat is a real-time monitoring system. In `CalculateAlarm.java`, `AviatorEvaluator` is used to directly execute the expression function, and no security policy is configured, resulting in AviatorScript (which can execute any static method by default) script injection. Version 1.4.1 fixes this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/51xxx/CVE-2023-51388.json
- https://github.com/dromara/hertzbeat/security/advisories/GHSA-mcqg-gqxr-hqgj
- https://nvd.nist.gov/vuln/detail/CVE-2023-51388
- https://github.com/dromara/hertzbeat/commit/8dcf050e27ca95d15460a7ba98a3df8a9cd1d3d2
