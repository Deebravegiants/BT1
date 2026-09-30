# [M] cJSON JSON Patch copy/add Uncontrolled Recursion Stack Exhaustion

## Summary
Severity: Medium
Advisory: CVE-2026-67215
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/CVE-2026-67215
Type: osv

## Details
cJSON through 1.7.19 is vulnerable to uncontrolled recursion leading to stack exhaustion when an untrusted RFC 6902 JSON Patch is applied via cJSONUtils_ApplyPatches() or cJSONUtils_ApplyPatchesCaseSensitive(). A patch containing add and copy operations grafts duplicated subtrees to amplify document depth beyond the parser's nesting limit: cJSON_Delete() recurses with no depth bound, and the cJSON_Duplicate() guard CJSON_CIRCULAR_LIMIT is set to 10000, ten times the parser's 1000-level nesting limit and high enough to overflow a default thread stack. An attacker who can supply the patch document can crash the process, resulting in denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67215.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-67215
- https://www.vulncheck.com/advisories/cjson-json-patch-copy-add-uncontrolled-recursion-stack-exhaustion
- https://github.com/DaveGamble/cJSON/blob/v1.7.19/cJSON.c#L253-L261
- https://github.com/DaveGamble/cJSON/blob/v1.7.19/cJSON_Utils.c#L906-L940
- https://joshua.hu/cjson-json-parser-cve-vulnerabilities
