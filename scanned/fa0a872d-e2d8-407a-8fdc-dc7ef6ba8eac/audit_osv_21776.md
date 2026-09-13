# [H] CVE-2021-46359

## Summary
Severity: High
Advisory: CVE-2021-46359
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-02-07
Source: https://osv.dev/vulnerability/CVE-2021-46359
Type: osv

## Details
FISCO-BCOS release-3.0.0-rc2 contains a denial of service vulnerability. Some transactions may not be committed successfully, and malicious users may use this to achieve double-spending attacks.

## References
- https://github.com/FISCO-BCOS/FISCO-BCOS/issues/2124
