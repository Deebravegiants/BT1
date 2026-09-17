# [M] CSRF protection on user_oidc login returned the expected token in case of an error

## Summary
Severity: Medium
Advisory: CVE-2023-28848
Aliases: GHSA-52hv-xw32-wf7f
CVSS: 4.8 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N)
Published: 2023-04-04
Source: https://osv.dev/vulnerability/CVE-2023-28848
Type: osv

## Details
user_oidc is the OIDC connect user backend for Nextcloud, an open source collaboration platform. A vulnerability in versions 1.0.0 until 1.3.0 effectively allowed an attacker to bypass the state protection as they could just copy the expected state token from the first request to their second request. Users should upgrade user_oidc to 1.3.0 to receive a patch for the issue. No known workarounds are available.

## References
- https://hackerone.com/reports/1878381
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28848.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-52hv-xw32-wf7f
- https://nvd.nist.gov/vuln/detail/CVE-2023-28848
- https://github.com/nextcloud/user_oidc/pull/580
