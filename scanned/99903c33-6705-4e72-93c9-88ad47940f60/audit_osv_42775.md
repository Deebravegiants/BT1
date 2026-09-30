# [C] nanoMODBUS Server-Side Out-of-Bounds Write in handle_read_file_record()

## Summary
Severity: Critical
Advisory: CVE-2026-71254
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71254
Type: osv

## Details
nanoMODBUS through v1.23.0 contains an out-of-bounds write in the Modbus server-side handle_read_file_record function (FC 0x14, Read File Record) in nanomodbus.c. The function validates that the total request size does not exceed 245 bytes and that each sub-request's record_length is at most 124, but it never validates the CUMULATIVE response size across all sub-requests before processing them.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71254.json
- https://github.com/debevv/nanoMODBUS
- https://github.com/debevv/nanoMODBUS/blob/master/nanomodbus.c
- https://nvd.nist.gov/vuln/detail/CVE-2026-71254
