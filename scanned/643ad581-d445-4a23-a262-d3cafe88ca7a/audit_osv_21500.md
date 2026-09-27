# [C] CVE-2021-43572

## Summary
Severity: Critical
Advisory: CVE-2021-43572
Aliases: GHSA-92vm-mxjf-jqf3, PYSEC-2021-426
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-11-09
Source: https://osv.dev/vulnerability/CVE-2021-43572
Type: osv

## Details
The verify function in the Stark Bank Python ECDSA library (aka starkbank-escada or ecdsa-python) before 2.0.1 fails to check that the signature is non-zero, which allows attackers to forge signatures on arbitrary messages.

## References
- https://github.com/starkbank/ecdsa-python/releases/tag/v2.0.1
- https://github.com/starkbank/ecdsa-python/commit/d136170666e9510eb63c2572551805807bd4c17f
- https://research.nccgroup.com/2021/11/08/technical-advisory-arbitrary-signature-forgery-in-stark-bank-ecdsa-libraries/
