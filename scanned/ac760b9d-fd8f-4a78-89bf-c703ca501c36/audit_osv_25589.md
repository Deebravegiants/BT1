# [M] Issuer not verified from obtained token in user_oidc

## Summary
Severity: Medium
Advisory: CVE-2023-39953
Aliases: GHSA-xx3h-v363-q36j
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2023-08-10
Source: https://osv.dev/vulnerability/CVE-2023-39953
Type: osv

## Details
user_oidc provides the OIDC connect user backend for Nextcloud, an open-source cloud platform. Starting in version 1.0.0 and prior to version 1.3.3, missing verification of the issuer would have allowed an attacker to perform a man-in-the-middle attack returning corrupted or known token they also have access to. user_oidc 1.3.3 contains a patch. No known workarounds are available.

## References
- https://hackerone.com/reports/2021684
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/39xxx/CVE-2023-39953.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-xx3h-v363-q36j
- https://nvd.nist.gov/vuln/detail/CVE-2023-39953
- https://github.com/nextcloud/user_oidc/pull/642
