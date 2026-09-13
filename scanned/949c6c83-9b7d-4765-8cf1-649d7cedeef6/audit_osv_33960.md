# [M] CVE-2025-53073

## Summary
Severity: Medium
Advisory: CVE-2025-53073
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-06-24
Source: https://osv.dev/vulnerability/CVE-2025-53073
Type: osv

## Details
In Sentry 25.1.0 through 25.5.1, an authenticated attacker can access a project's issue endpoint and perform unauthorized actions (such as adding a comment) without being a member of the project's team. A seven-digit issue ID must be known (it is not treated as a secret and might be mentioned publicly, or it could be predicted).

## References
- https://github.com/nikolas-ch/CVEs/blob/main/Sentry_Version%3E%3D25.1.0/Sentry_%3E%3D25.1.0_WeakAuthorizationControl.txt
- https://github.com/nikolas-ch/CVEs/tree/main/Sentry_Version%3E%3D25.1.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53073.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-53073
- https://github.com/getsentry/self-hosted/releases
