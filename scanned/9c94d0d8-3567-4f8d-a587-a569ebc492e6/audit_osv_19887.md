# [H] CVE-2021-27343

## Summary
Severity: High
Advisory: CVE-2021-27343
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-04-06
Source: https://osv.dev/vulnerability/CVE-2021-27343
Type: osv

## Details
SerenityOS Unspecified is affected by: Buffer Overflow. The impact is: obtain sensitive information (context-dependent). The component is: /Userland/Libraries/LibCrypto/ASN1/DER.h Crypto::der_decode_sequence() function. The attack vector is: Parsing RSA Key ASN.1.

## References
- https://github.com/SerenityOS/serenity/commit/48fbf6a88d4822a1e5470cf08f29464511bd72c1
- https://github.com/SerenityOS/serenity/issues/5317
- https://github.com/SerenityOS/serenity/pull/5344
- https://github.com/SerenityOS/serenity/commit/48fbf6a88d4822a1e5470cf08f29464511bd72c1
