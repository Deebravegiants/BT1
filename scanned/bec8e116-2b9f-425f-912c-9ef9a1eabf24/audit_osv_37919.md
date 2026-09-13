# [H] Authenticator vulnerable to Remote Code Execution

## Summary
Severity: High
Advisory: CVE-2026-33874
Aliases: GHSA-mjgm-7hwc-qqcr
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-33874
Type: osv

## Details
Gematik Authenticator securely authenticates users for login to digital health applications. Starting in version 4.12.0 and prior to version 4.16.0, the Mac OS version of the Authenticator is vulnerable to remote code execution, triggered when victims open a malicious file. Update the gematik Authenticator to version 4.16.0 or greater to receive a patch. There are no known workarounds.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33874.json
- https://github.com/gematik/app-Authenticator/security/advisories/GHSA-mjgm-7hwc-qqcr
- https://nvd.nist.gov/vuln/detail/CVE-2026-33874
- https://www.machinespirits.de/advisory/2e655e/
