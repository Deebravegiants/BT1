# [M] API key leak in codeium-chrome

## Summary
Severity: Medium
Advisory: CVE-2024-28120
Aliases: GHSA-8c7j-2h97-q63p
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2024-03-11
Source: https://osv.dev/vulnerability/CVE-2024-28120
Type: osv

## Details
codeium-chrome is an open source code completion plugin for the chrome web browser. The service worker of the codeium-chrome extension doesn't check the sender when receiving an external message. This allows an attacker to host a website that will steal the user's Codeium api-key, and thus impersonate the user on the backend autocomplete server. This issue has not been addressed. Users are advised to monitor the usage of their API key.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/28xxx/CVE-2024-28120.json
- https://github.com/Exafunction/codeium-chrome/security/advisories/GHSA-8c7j-2h97-q63p
- https://nvd.nist.gov/vuln/detail/CVE-2024-28120
- https://securitylab.github.com/advisories/GHSL-2024-027_GHSL-2024-028_codeium-chrome
