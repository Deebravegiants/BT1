# [M] Cleartext Transmission of Sensitive Information in user_oidc

## Summary
Severity: Medium
Advisory: CVE-2022-39339
Aliases: GHSA-2vff-cq8h-chhg
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2022-11-25
Source: https://osv.dev/vulnerability/CVE-2022-39339
Type: osv

## Details
user_oidc is an OpenID Connect user backend for Nextcloud. In versions prior to 1.2.1 sensitive information such as the OIDC client credentials and tokens are sent in plain text of HTTP without TLS. Any malicious actor with access to monitor user traffic may have been able to compromise account security. This issue has been addressed in in user_oidc v1.2.1. Users are advised to upgrade. Users unable to upgrade may use https to access Nextcloud. Set an HTTPS discovery URL in the provider settings (in Nextcloud OIDC admin settings).

## References
- https://hackerone.com/reports/1687005
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39339.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-2vff-cq8h-chhg
- https://nvd.nist.gov/vuln/detail/CVE-2022-39339
- https://github.com/nextcloud/user_oidc/pull/495
