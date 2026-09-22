# [M] WeGIA: Use of Weak Password Hashing Algorithm (SHA-256, no salt) in html/login.php

## Summary
Severity: Medium
Advisory: CVE-2026-45027
Aliases: GHSA-hcgv-vmq6-j6qg
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45027
Type: osv

## Details
WeGIA is a web manager for charitable institutions. In versions prior to 3.7.3, when a user logs in, html/login.php hashes the submitted password using PHP's hash() function with the SHA-256 algorithm and no salt before comparing it to the stored value. The password change flow in controle/FuncionarioControle.php follows the same pattern. SHA-256 is a general-purpose cryptographic hash built for speed, not password storage. Without a salt, identical passwords produce identical digests, making the entire hash database vulnerable to a single precomputed rainbow table lookup. This vulnerability is fixed in 3.7.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45027.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-hcgv-vmq6-j6qg
- https://nvd.nist.gov/vuln/detail/CVE-2026-45027
