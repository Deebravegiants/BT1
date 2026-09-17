# [H] ALPINE-CVE-2026-31790

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-31790
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-31790
Type: osv

## Affected
- Alpine:v3.20: `openssl` — affected >=3.0.0 <3.3.7-r0
- Alpine:v3.21: `openssl` — affected >=3.0.0 <3.3.7-r0
- Alpine:v3.22: `openssl` — affected >=3.0.0 <3.5.6-r0
- Alpine:v3.23: `openssl` — affected >=3.0.0 <3.5.6-r0
- Alpine:v3.24: `openssl` — affected >=3.0.0 <3.5.6-r0

## Details
Issue summary: Applications using RSASVE key encapsulation to establish
a secret encryption key can send contents of an uninitialized memory buffer to
a malicious peer.

Impact summary: The uninitialized buffer might contain sensitive data from the
previous execution of the application process which leads to sensitive data
leakage to an attacker.

RSA_public_encrypt() returns the number of bytes written on success and -1
on error. The affected code tests only whether the return value is non-zero.
As a result, if RSA encryption fails, encapsulation can still return success to
the caller, set the output lengths, and leave the caller to use the contents of
the ciphertext buffer as if a valid KEM ciphertext had been produced.

If applications use EVP_PKEY_encapsulate() with RSA/RSASVE on an
attacker-supplied invalid RSA public key without first validating that key,
then this may cause stale or uninitialized contents of the caller-provided
ciphertext buffer to be disclosed to the attacker in place of the KEM
ciphertext.

As a workaround calling EVP_PKEY_public_check() or
EVP_PKEY_public_check_quick() before EVP_PKEY_encapsulate() will mitigate
the issue.

The FIPS modules in 3.6, 3.5, 3.4, 3.3, 3.1 and 3.0 are affected by this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-31790
