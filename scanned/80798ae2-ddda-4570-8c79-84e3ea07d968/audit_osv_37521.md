# [H] Incorrect Failure Handling in RSA KEM RSASVE Encapsulation

## Summary
Severity: High
Advisory: CVE-2026-31790
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-31790
Type: osv

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
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31790.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31790
- https://openssl-library.org/news/secadv/20260407.txt
- https://github.com/openssl/openssl/commit/001e01db3e996e13ffc72386fe79d03a6683b5ac
- https://github.com/openssl/openssl/commit/abd8b2eec7e3f3fda60ecfb68498b246b52af482
- https://github.com/openssl/openssl/commit/b922e24e5b23ffb9cb9e14cadff23d91e9f7e406
- https://github.com/openssl/openssl/commit/d5f8e71cd0a54e961d0c3b174348f8308486f790
- https://github.com/openssl/openssl/commit/eed200f58cd8645ed77e46b7e9f764e284df379e
