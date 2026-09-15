# [M] Possible NULL Dereference in Password-Based CMS Decryption

## Summary
Severity: Medium
Advisory: CVE-2026-42766
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-42766
Type: osv

## Details
Issue summary: A specially crafted password-encrypted CMS message
can trigger a NULL pointer dereference during CMS decryption.

Impact summary: This NULL pointer dereference leads to an application crash
and a Denial of Service.

The CMS PasswordRecipientInfo.keyDerivationAlgorithm field is defined as
OPTIONAL in the ASN.1 specification and may therefore be absent in specially
crafted inputs. During the password-based CMS decryption the OpenSSL
CMS implementation dereferences this field without first checking whether it
was present.

An attacker who supplies such a CMS message to an application performing
password-based CMS decryption can trigger an application crash, leading to
a Denial of Service.

Applications that process password-encrypted CMS messages may be affected.

The FIPS modules in 4.0, 3.6, 3.5, 3.4, and 3.0 are not affected by this
issue, as the affected code is outside the OpenSSL FIPS module boundary.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42766.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-42766
- https://openssl-library.org/news/secadv/20260609.txt
- https://github.com/openssl/openssl/commit/056d06c1918fafbb98c1c85a02e4c47cc4e199ce
- https://github.com/openssl/openssl/commit/12bc26ffb3a2be728c9b86e1cae277de5b33dfa4
- https://github.com/openssl/openssl/commit/3ff64913615d648cfbb6a6f1cf5529ae7ea829d7
- https://github.com/openssl/openssl/commit/ab52d88cb5374876d59aee3c91f9e4ccce2b7ce4
- https://github.com/openssl/openssl/commit/da26f368732b83e40e9d356fe61c3d3aaab6d2e8
