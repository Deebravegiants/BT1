# [M] CubeCart Unauthorized Newsletter Unsubscription via force_unsubscribe Parameter

## Summary
Severity: Medium
Advisory: CVE-2025-59413
Aliases: GHSA-869v-gjv8-9m7f
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2025-09-22
Source: https://osv.dev/vulnerability/CVE-2025-59413
Type: osv

## Details
CubeCart is an ecommerce software solution. Prior to version 6.5.11, a logic flaw exists in the newsletter subscription endpoint that allows an attacker to unsubscribe any user without their consent. By changing the value of the force_unsubscribe parameter in the POST request to 1, an attacker can force the removal of any valid subscriber’s email address. This issue has been patched in version 6.5.11.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59413.json
- https://github.com/cubecart/v6/security/advisories/GHSA-869v-gjv8-9m7f
- https://nvd.nist.gov/vuln/detail/CVE-2025-59413
- https://github.com/cubecart/v6/commit/7fd1cd04f5d5c3ce1d7980327464f0ff6551de79
- https://github.com/cubecart/v6/commit/db965fcfa260c4f17eb16f8c5494e5af4a8ac271
- https://github.com/cubecart/v6/commit/dbc58cf1f7a6291f7add5893b56bff7920a29128
