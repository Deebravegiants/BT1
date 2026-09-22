# [M] CVE-2024-33255

## Summary
Severity: Medium
Advisory: CVE-2024-33255
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-26
Source: https://osv.dev/vulnerability/CVE-2024-33255
Type: osv

## Details
Jerryscript commit cefd391 was discovered to contain an Assertion Failure via ECMA_STRING_IS_REF_EQUALS_TO_ONE (string_p) in ecma_free_string_list.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/33xxx/CVE-2024-33255.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-33255
- https://github.com/jerryscript-project/jerryscript/issues/5135
