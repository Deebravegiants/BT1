# [H] nanoMODBUS Client-Side Out-of-Bounds Write via object_length in recv_read_device_identification_res()

## Summary
Severity: High
Advisory: CVE-2026-71255
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71255
Type: osv

## Details
nanoMODBUS through v1.23.0 contains an out-of-bounds write in the Modbus client-side recv_read_device_identification_res function (FC 0x2B/MEI 0x0E, Read Device Identification) in nanomodbus.c. The server-supplied object_length field (0-246) is validated only against the remaining PDU size (res_size_left) and is never validated against the caller-supplied buffers_length parameter.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71255.json
- https://github.com/debevv/nanoMODBUS
- https://github.com/debevv/nanoMODBUS/blob/master/nanomodbus.c
- https://nvd.nist.gov/vuln/detail/CVE-2026-71255
