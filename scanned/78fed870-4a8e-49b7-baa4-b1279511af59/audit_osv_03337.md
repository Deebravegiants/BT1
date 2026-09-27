# [C] ALPINE-CVE-2025-57052

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2025-57052
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-57052
Type: osv

## Affected
- Alpine:v3.19: `cjson` — affected >=1.5.0 <1.7.19-r0
- Alpine:v3.20: `cjson` — affected >=1.5.0 <1.7.19-r0
- Alpine:v3.21: `cjson` — affected >=1.5.0 <1.7.19-r0
- Alpine:v3.22: `cjson` — affected >=1.5.0 <1.7.19-r0
- Alpine:v3.23: `cjson` — affected >=1.5.0 <1.7.19-r0
- Alpine:v3.24: `cjson` — affected >=1.5.0 <1.7.19-r0

## Details
cJSON 1.5.0 through 1.7.18 allows out-of-bounds access via the decode_array_index_from_pointer function in cJSON_Utils.c, allowing remote attackers to bypass array bounds checking and access restricted data via malformed JSON pointer strings containing alphanumeric characters.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-57052
