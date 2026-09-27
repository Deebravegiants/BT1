# [H] CubeCart Session Not Invalidated After Password Change

## Summary
Severity: High
Advisory: CVE-2025-59335
Aliases: GHSA-4vwh-x8m2-fmvv
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-09-22
Source: https://osv.dev/vulnerability/CVE-2025-59335
Type: osv

## Details
CubeCart is an ecommerce software solution. Prior to version 6.5.11, there is an absence of automatic session expiration following a user's password change. This oversight poses a security risk, as if a user forgets to log out from a location where they accessed their account, an unauthorized user can maintain access even after the password has been changed. Due to this bug, if an account has already been compromised, the legitimate user has no way to revoke the attacker’s access. The malicious actor retains full access to the account until their session naturally expires. This means the account remains insecure even after the password has been changed. This issue has been patched in version 6.5.11.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59335.json
- https://github.com/cubecart/v6/security/advisories/GHSA-4vwh-x8m2-fmvv
- https://nvd.nist.gov/vuln/detail/CVE-2025-59335
- https://github.com/cubecart/v6/commit/4bfaeb4485dd82255a108940a163af5ba4583b52
- https://github.com/cubecart/v6/commit/62d9be8416aa6fd7343f8932d98c5b112b163e26
