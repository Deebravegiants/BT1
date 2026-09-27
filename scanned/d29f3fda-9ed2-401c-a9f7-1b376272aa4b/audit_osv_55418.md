# [C] CVE-2025-45765

## Summary
Severity: Critical
Advisory: CVE-2025-45765
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-08-07
Source: https://osv.dev/vulnerability/CVE-2025-45765
Type: osv

## Details
ruby-jwt v3.0.0.beta1 was discovered to contain weak encryption. NOTE: the Supplier's perspective is "keysize is not something that is enforced by this library. Currently more recent versions of OpenSSL are enforcing some key sizes and those restrictions apply to the users of this gem also."

## References
- https://gist.github.com/ZupeiNie/c621253068ce5b64911629534879e8f9
- https://github.com/jwt/ruby-jwt/issues/668
