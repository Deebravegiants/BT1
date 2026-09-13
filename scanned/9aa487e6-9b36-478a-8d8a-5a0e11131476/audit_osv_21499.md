# [C] CVE-2021-43570

## Summary
Severity: Critical
Advisory: CVE-2021-43570
Aliases: GHSA-r28h-x6hv-2fq3
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-11-09
Source: https://osv.dev/vulnerability/CVE-2021-43570
Type: osv

## Details
The verify function in the Stark Bank Java ECDSA library (ecdsa-java) 1.0.0 fails to check that the signature is non-zero, which allows attackers to forge signatures on arbitrary messages.

## References
- https://github.com/starkbank/ecdsa-java/releases/tag/v1.0.1
- https://research.nccgroup.com/2021/11/08/technical-advisory-arbitrary-signature-forgery-in-stark-bank-ecdsa-libraries/
