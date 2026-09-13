# [H] Possible NULL Dereference When Processing CMS KeyAgreeRecipientInfo

## Summary
Severity: High
Advisory: CVE-2026-28389
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-28389
Type: osv

## Details
Issue summary: During processing of a crafted CMS EnvelopedData message
with KeyAgreeRecipientInfo a NULL pointer dereference can happen.

Impact summary: Applications that process attacker-controlled CMS data may
crash before authentication or cryptographic operations occur resulting in
Denial of Service.

When a CMS EnvelopedData message that uses KeyAgreeRecipientInfo is
processed, the optional parameters field of KeyEncryptionAlgorithmIdentifier
is examined without checking for its presence. This results in a NULL
pointer dereference if the field is missing.

Applications and services that call CMS_decrypt() on untrusted input
(e.g., S/MIME processing or CMS-based protocols) are vulnerable.

The FIPS modules in 3.6, 3.5, 3.4, 3.3 and 3.0 are not affected by this
issue, as the affected code is outside the OpenSSL FIPS module boundary.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28389.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-28389
- https://openssl-library.org/news/secadv/20260407.txt
- https://github.com/openssl/openssl/commit/16cea4188e0ea567deb4f93f85902247e67384f5
- https://github.com/openssl/openssl/commit/785cbf7ea3b5a6f5adf0c1ccb92b79d89c35c616
- https://github.com/openssl/openssl/commit/7b5274e812400cacb6f3be4c2df5340923fa807f
- https://github.com/openssl/openssl/commit/c6725634e089eb2b634b10ede33944be7248172a
- https://github.com/openssl/openssl/commit/f80f83bc5fd036bc47d773e8b15a001e2b4ce686
