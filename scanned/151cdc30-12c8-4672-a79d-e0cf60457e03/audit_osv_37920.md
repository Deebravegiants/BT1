# [C] Authenticator Vulnerable to Authentication Flow Hijack

## Summary
Severity: Critical
Advisory: CVE-2026-33875
Aliases: GHSA-qg87-cf56-2rmr
CVSS: 9.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-33875
Type: osv

## Details
Gematik Authenticator securely authenticates users for login to digital health applications. Versions prior to 4.16.0 are vulnerable to authentication flow hijacking, potentially allowing attackers to authenticate with the identities of victim users who click on a malicious deep link. Update Gematik Authenticator to version 4.16.0 or greater to receive a patch. There are no known workarounds.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33875.json
- https://github.com/gematik/app-Authenticator/security/advisories/GHSA-qg87-cf56-2rmr
- https://nvd.nist.gov/vuln/detail/CVE-2026-33875
- https://www.machinespirits.com/advisory/f41e56/
