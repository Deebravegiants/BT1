# [H] ALPINE-CVE-2020-14382

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-14382
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-09-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-14382
Type: osv

## Affected
- Alpine:v3.11: `cryptsetup` — affected >=0 <2.2.2-r1
- Alpine:v3.12: `cryptsetup` — affected >=0 <2.3.2-r1
- Alpine:v3.13: `cryptsetup` — affected >=0 <2.3.4-r0
- Alpine:v3.14: `cryptsetup` — affected >=0 <2.3.4-r0
- Alpine:v3.15: `cryptsetup` — affected >=0 <2.3.4-r0
- Alpine:v3.16: `cryptsetup` — affected >=0 <2.3.4-r0
- Alpine:v3.17: `cryptsetup` — affected >=0 <2.3.4-r0
- Alpine:v3.18: `cryptsetup` — affected >=0 <2.3.4-r0
- Alpine:v3.19: `cryptsetup` — affected >=0 <2.3.4-r0
- Alpine:v3.20: `cryptsetup` — affected >=0 <2.3.4-r0
- Alpine:v3.21: `cryptsetup` — affected >=0 <2.3.4-r0
- Alpine:v3.22: `cryptsetup` — affected >=0 <2.3.4-r0
- Alpine:v3.23: `cryptsetup` — affected >=0 <2.3.4-r0
- Alpine:v3.24: `cryptsetup` — affected >=0 <2.3.4-r0

## Details
A vulnerability was found in upstream release cryptsetup-2.2.0 where, there's a bug in LUKS2 format validation code, that is effectively invoked on every device/image presenting itself as LUKS2 container. The bug is in segments validation code in file 'lib/luks2/luks2_json_metadata.c' in function hdr_validate_segments(struct crypt_device *cd, json_object *hdr_jobj) where the code does not check for possible overflow on memory allocation used for intervals array (see statement "intervals = malloc(first_backup * sizeof(*intervals));"). Due to the bug, library can be *tricked* to expect such allocation was successful but for far less memory then originally expected. Later it may read data FROM image crafted by an attacker and actually write such data BEYOND allocated memory.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-14382
