# [C] nanoMODBUS Client-Side Out-of-Bounds Read Leading to Wild-Pointer Write via object_id

## Summary
Severity: Critical
Advisory: CVE-2026-71256
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71256
Type: osv

## Details
nanoMODBUS through v1.23.0 contains an out-of-bounds stack read leading to a wild-pointer write in nmbs_read_device_identification_basic / recv_read_device_identification_res in nanomodbus.c. A fixed 3-element stack array order[3] = {0,1,2} maps object IDs to buffer indices. The server-supplied object_id field (0-255, read directly from the wire) is used without any bounds check as buf_index = order[object_id].

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71256.json
- https://github.com/debevv/nanoMODBUS
- https://github.com/debevv/nanoMODBUS/blob/master/nanomodbus.c
- https://nvd.nist.gov/vuln/detail/CVE-2026-71256
