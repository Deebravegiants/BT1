# [M] Potential share collision for recipients when caching is enabled in nextcloud server

## Summary
Severity: Medium
Advisory: CVE-2023-28643
Aliases: GHSA-hhq4-4pr8-wm27
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2023-03-30
Source: https://osv.dev/vulnerability/CVE-2023-28643
Type: osv

## Details
Nextcloud server is an open source home cloud implementation. In affected versions when a recipient receives 2 shares with the same name, while a memory cache is configured, the second share will replace the first one instead of being renamed to `{name} (2)`. It is recommended that the Nextcloud Server is upgraded to 25.0.3 or 24.0.9. Users unable to upgrade should avoid sharing 2 folders with the same name to the same user.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28643.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-hhq4-4pr8-wm27
- https://nvd.nist.gov/vuln/detail/CVE-2023-28643
- https://github.com/nextcloud/server/issues/34015
- https://github.com/nextcloud/server/pull/36047
