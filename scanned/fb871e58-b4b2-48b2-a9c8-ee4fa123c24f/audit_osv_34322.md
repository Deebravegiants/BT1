# [C] FreshRSS vulnerable to authenticated RCE via path traversal inside include()

## Summary
Severity: Critical
Advisory: CVE-2025-58173
Aliases: GHSA-6c8h-w3j5-j293
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-12-15
Source: https://osv.dev/vulnerability/CVE-2025-58173
Type: osv

## Details
FreshRSS is a self-hosted RSS feed aggregator. In versions 1.23.0 through 1.27.0, using a path traversal inside the `language` user configuration parameter, it's possible to call `install.php` and perform various administrative actions as an unprivileged user. These actions include logging in as the admin, creating a new admin user, or set the database to an attacker-controlled MySQL server and abuse it to execute code in FreshRSS by setting malicious feed `curl_params` inside the `feed` table. Version 1.27.1 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58173.json
- https://github.com/FreshRSS/FreshRSS/security/advisories/GHSA-6c8h-w3j5-j293
- https://nvd.nist.gov/vuln/detail/CVE-2025-58173
- https://github.com/FreshRSS/FreshRSS/commit/79604aa4b3051f083d1734bd9e82c6a89d785c5a#diff-49280171b6e7964e21a0270427e56eacb47b8ac562593a01ad4bc74b49f840c7R135
- https://github.com/FreshRSS/FreshRSS/commit/dbbae15a8458679db0f4540dacdbdcff9c02ec8c#diff-63f610c36d0f2555c1787f6d0804f46f4df6e0f918dfe03408309039abf6efebL85-L88
- https://github.com/FreshRSS/FreshRSS/commit/ee175dd6169a016fc898fac62d046e22c205dec0#diff-6ebff7743ede829cf5a7f0e4566b42023a2d4779cc8d7e96fefec116f2292174R190-R194
- https://github.com/FreshRSS/FreshRSS/pull/7878
- https://github.com/FreshRSS/FreshRSS/pull/7971
- https://github.com/FreshRSS/FreshRSS/pull/7979
