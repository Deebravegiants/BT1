# [H] CVE-2020-16162

## Summary
Severity: High
Advisory: CVE-2020-16162
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-07-30
Source: https://osv.dev/vulnerability/CVE-2020-16162
Type: osv

## Details
An issue was discovered in RIPE NCC RPKI Validator 3.x through 3.1-2020.07.06.14.28. Missing validation checks on CRL presence or CRL staleness in the X509-based RPKI certificate-tree validation procedure allow remote attackers to bypass intended access restrictions by using revoked certificates. NOTE: there may be counterarguments related to backwards compatibility

## References
- https://github.com/RIPE-NCC/rpki-validator-3/issues/162
- https://github.com/RIPE-NCC/rpki-validator-3/issues/232
