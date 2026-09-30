# [C] Donetick Has Weak Default JWT Secret

## Summary
Severity: Critical
Advisory: CVE-2025-47945
Aliases: GHSA-hjjg-vw4j-986x
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-05-17
Source: https://osv.dev/vulnerability/CVE-2025-47945
Type: osv

## Details
Donetick an open-source app for managing tasks and chores. Prior to version 0.1.44, the application uses JSON Web Tokens (JWT) for authentication, but the signing secret has a weak default value. While the responsibility is left to the system administrator to change it, this approach is inadequate. The vulnerability is proven by existence of the issue in the live version as well. This issue can result in full account takeover of any user. Version 0.1.44 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/47xxx/CVE-2025-47945.json
- https://github.com/donetick/donetick/security/advisories/GHSA-hjjg-vw4j-986x
- https://nvd.nist.gov/vuln/detail/CVE-2025-47945
- https://github.com/donetick/donetick/commit/620b897bc0135f6668bb8a5562678104531108eb
- https://github.com/donetick/donetick/commit/b9a6e177eefdc605dedbc5320f0d93d6573d1db6
