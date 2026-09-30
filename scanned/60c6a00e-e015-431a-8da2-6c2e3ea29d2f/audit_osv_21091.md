# [M] CVE-2021-40559

## Summary
Severity: Medium
Advisory: CVE-2021-40559
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-12
Source: https://osv.dev/vulnerability/CVE-2021-40559
Type: osv

## Details
A null pointer deference vulnerability exists in gpac through 1.0.1 via the naludmx_parse_nal_avc function in reframe_nalu, which allows a denail of service.

## References
- https://www.debian.org/security/2023/dsa-5411
- https://github.com/gpac/gpac/issues/1886
