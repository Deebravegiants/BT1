# [C] Arbitrary code execution due to improper sanitization of web app properties in PWAsForFirefox

## Summary
Severity: Critical
Advisory: CVE-2024-32986
Aliases: GHSA-jmhv-m7v5-g5jq
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2024-05-03
Source: https://osv.dev/vulnerability/CVE-2024-32986
Type: osv

## Details
PWAsForFirefox is a tool to install, manage and use Progressive Web Apps (PWAs) in Mozilla Firefox. Due to improper sanitization of web app properties (such as name, description, shortcuts), web apps were able to inject additional lines into XDG Desktop Entries (on Linux) and `AppInfo.ini` (on PortableApps.com). This allowed malicious web apps to introduce keys like `Exec`, which could run arbitrary code when the affected web app was launched. This vulnerability affects all Linux and PortableApps.com users of all PWAsForFirefox versions up to (excluding) 2.12.0. Windows and macOS users are not affected. This vulnerability has been fixed in commit `9932d4b` which has been included in release in v2.12.0. The main fix is implemented in the native part, but the extension also contains additional fixes. All Linux and PortableApps.com users are advised to update to this version as soon as possible. It is also recommended for Windows and macOS users to update to this version, as it contains additional fixes related to properties sanitization. There are no known workarounds for this vulnerability.

## References
- https://github.com/filips123/PWAsForFirefox/releases/tag/v2.12.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32986.json
- https://github.com/filips123/PWAsForFirefox/security/advisories/GHSA-jmhv-m7v5-g5jq
- https://nvd.nist.gov/vuln/detail/CVE-2024-32986
- https://github.com/filips123/PWAsForFirefox/commit/9932d4b289631d447f88ace09a2fabafe4cd5bd5
