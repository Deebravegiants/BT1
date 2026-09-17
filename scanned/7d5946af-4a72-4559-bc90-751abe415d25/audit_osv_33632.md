# [M] Nextcloud Server doesn't request second factor after session timeout

## Summary
Severity: Medium
Advisory: CVE-2025-47790
Aliases: GHSA-9h3w-f3h4-qqrh
CVSS: 6.4 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:N)
Published: 2025-05-16
Source: https://osv.dev/vulnerability/CVE-2025-47790
Type: osv

## Details
Nextcloud Server is a self hosted personal cloud system. Nextcloud Server prior to 29.0.15, 30.0.9, and 31.0.3 and Nextcloud Enterprise Server prior to 26.0.13.15, 27.1.11.15, 28.0.14.6, 29.0.15, 30.0.9, and 31.0.3 have a bug with session handling. The bug caused skipping the second factor confirmation after a successful login with the username and password when the server was configured with `remember_login_cookie_lifetime` set to `0`, once the session expired on the page to select the second factor and the page is reloaded. Nextcloud Server 29.0.15, 30.0.9, and 31.0.3 and Nextcloud Enterprise Server is upgraded to 26.0.13.15, 27.1.11.15, 28.0.14.6, 29.0.15, 30.0.9 and 31.0.3 contain a patch. As a workaround, set the `remember_login_cookie_lifetime` in config.php to a value other than `0`, e.g. `900`. Beware that this is only a workaround for new sessions created after the configuration change. System administration can delete affected sessions.

## References
- https://hackerone.com/reports/2729367
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/47xxx/CVE-2025-47790.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-9h3w-f3h4-qqrh
- https://nvd.nist.gov/vuln/detail/CVE-2025-47790
- https://github.com/nextcloud/server/pull/51905
