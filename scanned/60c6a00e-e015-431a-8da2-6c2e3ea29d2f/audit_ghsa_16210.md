# [H] Appwrite Directory Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-wfm3-gq9h-mrjm
CVE: CVE-2022-25377
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-02-23
Source: https://github.com/advisories/GHSA-wfm3-gq9h-mrjm
Type: github-advisory

## Affected
- Packagist: `appwrite/server-ce` — affected >=0.5.0 <0.12.2

## Details
The ACME-challenge endpoint in Appwrite 0.5.0 through 0.12.x before 0.12.2 allows remote attackers to read arbitrary local files via ../ directory traversal. In order to be vulnerable, `APP_STORAGE_CERTIFICATES/.well-known/acme-challenge` must exist on disk. (This pathname is automatically created if the user chooses to install Let's Encrypt certificates via Appwrite.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25377
- https://github.com/appwrite/appwrite/pull/2780
- https://github.com/appwrite/appwrite/commit/892f6fa4ba0d44e2435ffad1a84542400cfb7a9b
- https://dubell.io/unauthenticated-lfi-in-appwrite-0.5.0-0.12.1
- https://github.com/appwrite/appwrite
- https://github.com/appwrite/appwrite/blob/0.12.0/app/controllers/general.php#L539
- https://github.com/appwrite/appwrite/releases/tag/0.12.2
