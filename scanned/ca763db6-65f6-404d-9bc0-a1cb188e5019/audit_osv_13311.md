# [C] CVE-2018-19185

## Summary
Severity: Critical
Advisory: CVE-2018-19185
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-12
Source: https://osv.dev/vulnerability/CVE-2018-19185
Type: osv

## Details
An issue has been found in libIEC61850 v1.3. It is a heap-based buffer overflow in BerEncoder_encodeOctetString in mms/asn1/ber_encoder.c. This is exploitable even after CVE-2018-18834 has been patched, with a different dataSetValue sequence than the CVE-2018-18834 attack vector.

## References
- https://github.com/fouzhe/security/tree/master/libiec61850#another-heap-buffer-overflow-in-function-berencoder_encodeoctetstring
- https://github.com/mz-automation/libiec61850/issues/87
