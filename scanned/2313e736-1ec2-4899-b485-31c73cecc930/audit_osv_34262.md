# [C] CVE-2025-57052

## Summary
Severity: Critical
Advisory: CVE-2025-57052
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-03
Source: https://osv.dev/vulnerability/CVE-2025-57052
Type: osv

## Details
cJSON 1.5.0 through 1.7.18 allows out-of-bounds access via the decode_array_index_from_pointer function in cJSON_Utils.c, allowing remote attackers to bypass array bounds checking and access restricted data via malformed JSON pointer strings containing alphanumeric characters.

## References
- https://lists.debian.org/debian-lts-announce/2025/09/msg00019.html
- https://x-0r.com/posts/cJSON-Array-Index-Parsing-Vulnerability
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57052.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-57052
