# [H] Eclipse OMR: Buffer overflow vulnerability

## Summary
Severity: High
Advisory: CVE-2025-1471
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:L/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-02-21
Source: https://osv.dev/vulnerability/CVE-2025-1471
Type: osv

## Details
In Eclipse OMR versions 0.2.0 to 0.4.0, some of the z/OS atoe print functions use a constant length buffer for string conversion. If the input format string and arguments are larger than the buffer size then buffer overflow occurs.  Beginning in version 0.5.0, the conversion buffers are sized correctly and checked appropriately to prevent buffer overflows.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/1xxx/CVE-2025-1471.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-1471
- https://gitlab.eclipse.org/security/cve-assignement/-/issues/55
- https://github.com/eclipse-omr/omr/pull/7658
- https://github.com/eclipse-omr/omr
