# [C] CVE-2021-43569

## Summary
Severity: Critical
Advisory: CVE-2021-43569
Aliases: GHSA-j3jw-j2j8-2wv9
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-11-09
Source: https://osv.dev/vulnerability/CVE-2021-43569
Type: osv

## Details
The verify function in the Stark Bank .NET ECDSA library (ecdsa-dotnet) 1.3.1 fails to check that the signature is non-zero, which allows attackers to forge signatures on arbitrary messages.

## References
- https://github.com/starkbank/ecdsa-dotnet/releases/tag/v1.3.2
- https://research.nccgroup.com/2021/11/08/technical-advisory-arbitrary-signature-forgery-in-stark-bank-ecdsa-libraries/
