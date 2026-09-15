# [C] CVE-2021-4300

## Summary
Severity: Critical
Advisory: CVE-2021-4300
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-04
Source: https://osv.dev/vulnerability/CVE-2021-4300
Type: osv

## Details
A vulnerability has been found in ghostlander Halcyon and classified as critical. Affected by this vulnerability is the function CBlock::AddToBlockIndex of the file src/main.cpp of the component Block Verification. The manipulation leads to improper access controls. The attack can be launched remotely. Upgrading to version 1.1.1.0-hal is able to address this issue. The identifier of the patch is 0675b25ae9cc10b5fdc8ea3a32c642979762d45e. It is recommended to upgrade the affected component. The identifier VDB-217417 was assigned to this vulnerability.

## References
- https://github.com/ghostlander/Halcyon/releases/tag/v1.1.1.0-hal
- https://vuldb.com/?ctiid.217417
- https://vuldb.com/?id.217417
- https://github.com/ghostlander/Halcyon/commit/0675b25ae9cc10b5fdc8ea3a32c642979762d45e
