# [M] Nextcloud user_oidc's ID4me does not validate signature or expiration

## Summary
Severity: Medium
Advisory: CVE-2024-37886
Aliases: GHSA-vw5h-29xf-g55g
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2024-06-14
Source: https://osv.dev/vulnerability/CVE-2024-37886
Type: osv

## Details
user_oidc app is an OpenID Connect user backend for Nextcloud. An attacker could potentially trick the app into accepting a request that is not signed by the correct server. It is recommended that the Nextcloud user_oidc app is upgraded to 1.3.5, 2.0.0, 3.0.0, 4.0.0 or 5.0.0.

## References
- https://hackerone.com/reports/1878391
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/37xxx/CVE-2024-37886.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-vw5h-29xf-g55g
- https://nvd.nist.gov/vuln/detail/CVE-2024-37886
- https://github.com/nextcloud/user_oidc/pull/715
