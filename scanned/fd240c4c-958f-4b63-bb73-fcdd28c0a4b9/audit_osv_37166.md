# [M] cJSON 1.7.19 Wrong-Key Modification via JSON Pointer Escape Decoding

## Summary
Severity: Medium
Advisory: CVE-2026-29036
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-29036
Type: osv

## Details
cJSON versions 1.5.0 through 1.7.19 contain an incorrectly-resolved name or reference vulnerability in the decode_pointer_inplace() function within cJSON_Utils.c that allows unauthenticated attackers to cause JSON Patch operations to target wrong object keys by supplying crafted JSON Pointer escape sequences (~0 or ~1) in patch paths. Attackers can submit malicious RFC 6902 JSON Patch input to applications using cJSONUtils_ApplyPatches() or cJSONUtils_ApplyPatchesCaseSensitive() to silently corrupt data or delete unintended keys, potentially bypassing authorization controls in applications that rely on JSON Patch for access-controlled data modification.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29036.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-29036
- https://www.vulncheck.com/advisories/cjson-wrong-key-modification-via-json-pointer-escape-decoding
- https://github.com/DaveGamble/cJSON
