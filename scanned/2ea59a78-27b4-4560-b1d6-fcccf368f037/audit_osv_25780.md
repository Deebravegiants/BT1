# [H] Client-Side Request Forgery in Home Assistant iOS/macOS native Apps

## Summary
Severity: High
Advisory: CVE-2023-44385
Aliases: GHSA-h2jp-7grc-9xpp
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2023-10-19
Source: https://osv.dev/vulnerability/CVE-2023-44385
Type: osv

## Details
The Home Assistant Companion for iOS and macOS app up to version 2023.4 are vulnerable to Client-Side Request Forgery. Attackers may send malicious links/QRs to victims that, when visited, will make the victim to call arbitrary services in their Home Assistant installation. Combined with this security advisory, may result in full compromise and remote code execution (RCE). Version 2023.7 addresses this issue and all users are advised to upgrade. There are no known workarounds for this vulnerability. This issue is also tracked as GitHub Security Lab (GHSL) Vulnerability Report: GHSL-2023-161.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/44xxx/CVE-2023-44385.json
- https://github.com/home-assistant/core/security/advisories/GHSA-h2jp-7grc-9xpp
- https://nvd.nist.gov/vuln/detail/CVE-2023-44385
