# [H] crypto: ecdsa - Harden against integer overflows in DIV_ROUND_UP()

## Summary
Severity: High
Advisory: CVE-2025-37984
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-20
Source: https://osv.dev/vulnerability/CVE-2025-37984
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.99, >=6.7.0 <6.12.39, >=6.10.0 <6.14.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: ecdsa - Harden against integer overflows in DIV_ROUND_UP()

Herbert notes that DIV_ROUND_UP() may overflow unnecessarily if an ecdsa
implementation's ->key_size() callback returns an unusually large value.
Herbert instead suggests (for a division by 8):

  X / 8 + !!(X & 7)

Based on this formula, introduce a generic DIV_ROUND_UP_POW2() macro and
use it in lieu of DIV_ROUND_UP() for ->key_size() return values.

Additionally, use the macro in ecc_digits_from_bytes(), whose "nbytes"
parameter is a ->key_size() return value in some instances, or a
user-specified ASN.1 length in the case of ecdsa_get_signature_rs().

## References
- https://git.kernel.org/stable/c/921b8167f10708e38080f84e195cdc68a7a561f1
- https://git.kernel.org/stable/c/b16510a530d1e6ab9683f04f8fb34f2e0f538275
- https://git.kernel.org/stable/c/f02f0218be412cff1c844addf58e002071be298b
- https://git.kernel.org/stable/c/f2133b849ff273abddb6da622daddd8f6f6fa448
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37984.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37984
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
