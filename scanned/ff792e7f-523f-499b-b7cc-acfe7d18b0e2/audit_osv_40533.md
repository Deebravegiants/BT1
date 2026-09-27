# [H] Coturn: SQL Injection in HTTPS Admin Panel Delete Operations

## Summary
Severity: High
Advisory: CVE-2026-53448
Aliases: GHSA-v8hj-2xx7-xmp5
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-53448
Type: osv

## Details
Coturn is a free open source implementation of TURN and STUN Server. Prior to 4.12.0, the coturn HTTPS admin panel passes HTTP query parameters directly into SQL queries via snprintf string interpolation without sanitization. The is_secure_string filter that protects the STUN protocol path is not applied to the admin panel's delete-user, delete-secret, and delete-IP operations, so an authenticated admin can inject arbitrary SQL through the du, ds, and dip parameters, gaining full database control and potentially OS-level access via PostgreSQL COPY TO PROGRAM. This issue is fixed in version 4.12.0.

## References
- https://github.com/coturn/coturn/releases/tag/4.12.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53448.json
- https://github.com/coturn/coturn/security/advisories/GHSA-v8hj-2xx7-xmp5
- https://nvd.nist.gov/vuln/detail/CVE-2026-53448
- https://github.com/coturn/coturn/commit/b84dbab1d1aa6e2bf0211a1cdbb250d6de2a0d09
- https://github.com/coturn/coturn/pull/1924
