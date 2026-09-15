# [H] Encrypted ID token or JARM response accepted without a nested signature in erlef oidcc

## Summary
Severity: High
Advisory: CVE-2026-75759
Aliases: EEF-CVE-2026-75759, GHSA-533g-4vf3-xwrj
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-30
Source: https://osv.dev/vulnerability/CVE-2026-75759
Type: osv

## Details
Improper Verification of Cryptographic Signature vulnerability in erlef oidcc allows an unauthenticated attacker to impersonate an arbitrary user via an encrypted ID token or JARM response carrying no nested signature. OpenID Connect Core 1.0 section 2 requires that an encrypted ID token be signed then encrypted, with the result being a Nested JWT, and JARM processing rule 5 requires the client to check the signature unconditionally. oidcc instead accepted a JWE wrapping unsigned claims as fully validated, so anyone holding the relying party's public encryption key could mint a token with an arbitrary sub, iss, and aud without possessing the provider's signing key.

In oidcc_jwt_util:verify_decrypted_token/4, a decrypted payload that is not a signed JWS fell back to parsing the plaintext claims and returning them with no verifying key. oidcc_token:int_validate_jwt/4 then matched on the JOSE structure type rather than on whether a signature had been verified, and returned success. The JARM path in oidcc_token:validate_jarm/3 is reachable through the browser front channel. UserInfo responses are not affected, because OpenID Connect Core 1.0 section 5.3.2 permits them to be encrypted without also being signed.

This issue affects oidcc: from 3.2.0-beta.1 before 3.9.0.

## References
- https://cna.erlef.org/cves/CVE-2026-75759.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-75759
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75759.json
- https://github.com/erlef/oidcc/security/advisories/GHSA-533g-4vf3-xwrj
- https://nvd.nist.gov/vuln/detail/CVE-2026-75759
- https://github.com/erlef/oidcc/commit/5f62fbccdae8526ff62653b8901657a6c1400fd9
- https://github.com/erlef/oidcc
