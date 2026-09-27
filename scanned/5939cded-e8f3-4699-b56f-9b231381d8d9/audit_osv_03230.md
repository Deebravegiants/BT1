# [H] ALPINE-CVE-2025-25724

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-25724
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-25724
Type: osv

## Affected
- Alpine:v3.18: `libarchive` — affected >=0 <3.7.9-r0
- Alpine:v3.19: `libarchive` — affected >=0 <3.7.9-r0
- Alpine:v3.20: `libarchive` — affected >=0 <3.7.9-r0
- Alpine:v3.21: `libarchive` — affected >=0 <3.7.9-r0
- Alpine:v3.22: `libarchive` — affected >=0 <3.7.9-r0
- Alpine:v3.23: `libarchive` — affected >=0 <3.7.9-r0
- Alpine:v3.24: `libarchive` — affected >=0 <3.7.9-r0

## Details
list_item_verbose in tar/util.c in libarchive through 3.7.7 does not check an strftime return value, which can lead to a denial of service or unspecified other impact via a crafted TAR archive that is read with a verbose value of 2. For example, the 100-byte buffer may not be sufficient for a custom locale.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-25724
