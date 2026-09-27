# [H] ADB Explorer Vulnerable to RCE via Insufficient Input Validation

## Summary
Severity: High
Advisory: CVE-2026-26959
Aliases: GHSA-gcgv-2jq7-74rp
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-02-19
Source: https://osv.dev/vulnerability/CVE-2026-26959
Type: osv

## Details
ADB Explorer is a fluent UI for ADB on Windows. Versions 0.9.26020 and below fail to validate the integrity or authenticity of the ADB binary path specified in the ManualAdbPath setting before executing it, allowing arbitrary code execution with the privileges of the current user. An attacker can exploit this by crafting a malicious App.txt settings file that points ManualAdbPath to an arbitrary executable, then convincing a victim to launch the application with a command-line argument directing it to the malicious configuration directory. This vulnerability could be leveraged through social engineering tactics, such as distributing a shortcut bundled with a crafted settings file in an archive, resulting in RCE upon application startup. Thus issue has been fixed in version 0.9.26021.

## References
- https://github.com/Alex4SSB/ADB-Explorer/releases/tag/v0.9.26021
- https://github.com/Alex4SSB/ADB-Explorer/security/advisories/GHSA-gcgv-2jq7-74rp
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26959.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-26959
- https://github.com/Alex4SSB/ADB-Explorer/commit/1b9fed20e875f5e74fd04e9889402f969c2d34e4
