# [H] CVE-2019-6135

## Summary
Severity: High
Advisory: CVE-2019-6135
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-11
Source: https://osv.dev/vulnerability/CVE-2019-6135
Type: osv

## Details
An issue has been found in libIEC61850 v1.3.1. Memory_malloc in hal/memory/lib_memory.c has a memory leak when called from Asn1PrimitiveValue_create in mms/asn1/asn1_ber_primitive_value.c, as demonstrated by goose_publisher_example.c and iec61850_9_2_LE_example.c.

## References
- https://github.com/mz-automation/libiec61850/issues/103
- https://github.com/mz-automation/libiec61850/issues/104
