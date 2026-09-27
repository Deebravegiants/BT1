# [H] CVE-2024-36702

## Summary
Severity: High
Advisory: CVE-2024-36702
CVSS: 7.4 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-11
Source: https://osv.dev/vulnerability/CVE-2024-36702
Type: osv

## Details
libiec61850 v1.5 was discovered to contain a heap overflow via the BerEncoder_encodeLength function at /asn1/ber_encoder.c.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36702.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36702
- https://github.com/mz-automation/libiec61850/issues/505
- https://github.com/mz-automation/libiec61850
