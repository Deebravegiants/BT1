# [H] Possible NULL Dereference When Processing CMS KeyTransportRecipientInfo

## Summary
Severity: High
Advisory: CVE-2026-28390
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-28390
Type: osv

## Details
Issue summary: During processing of a crafted CMS EnvelopedData message
with KeyTransportRecipientInfo a NULL pointer dereference can happen.

Impact summary: Applications that process attacker-controlled CMS data may
crash before authentication or cryptographic operations occur resulting in
Denial of Service.

When a CMS EnvelopedData message that uses KeyTransportRecipientInfo with
RSA-OAEP encryption is processed, the optional parameters field of
RSA-OAEP SourceFunc algorithm identifier is examined without checking
for its presence. This results in a NULL pointer dereference if the field
is missing.

Applications and services that call CMS_decrypt() on untrusted input
(e.g., S/MIME processing or CMS-based protocols) are vulnerable.

The FIPS modules in 3.6, 3.5, 3.4, 3.3 and 3.0 are not affected by this
issue, as the affected code is outside the OpenSSL FIPS module boundary.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28390.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-28390
- https://openssl-library.org/news/secadv/20260407.txt
- https://github.com/openssl/openssl/commit/01194a8f1941115cd0383bfa91c736dd3993c8bc
- https://github.com/openssl/openssl/commit/2e39b7a6993be445fddb9fbce316fa756e0397b6
- https://github.com/openssl/openssl/commit/af2a5fecd3e71a29e7568f9c1453dec5cebbaff4
- https://github.com/openssl/openssl/commit/ea7b4ea4f9f853521ba34830cbcadc970d2e0788
- https://github.com/openssl/openssl/commit/fd2f1a6cf53b9ceeca723a001aa4b825d7c7ee75
