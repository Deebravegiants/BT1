# [H] ADB Explorer is Vulnerable to Arbitrary Directory Deletion via Command-Line Argument

## Summary
Severity: High
Advisory: CVE-2026-27115
Aliases: GHSA-rg2h-2p33-rxcr
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2026-02-20
Source: https://osv.dev/vulnerability/CVE-2026-27115
Type: osv

## Details
ADB Explorer is a fluent UI for ADB on Windows. Versions 0.9.26020 and below have an unvalidated command-line argument that allows any user to trigger recursive deletion of arbitrary directories on the Windows filesystem. ADB Explorer accepts an optional path argument to set a custom data directory, but only check whether the path exists. The ClearDrag() method calls Directory.Delete(dir, true) on every subdirectory of that path at both application startup and exit. An attacker can craft a malicious shortcut (.lnk) or batch script that launches ADB Explorer with a critical directory (e.g. C:\Users\%USERNAME%\Documents) as the argument, causing permanent recursive deletion of all its subdirectories. Any user who launches ADB Explorer via a crafted shortcut, batch file, or script loses the contents of the targeted directory permanently (deletion bypasses the Recycle Bin). This issue has been fixed in version 0.9.26021.

## References
- https://github.com/Alex4SSB/ADB-Explorer/releases/tag/v0.9.26021
- https://github.com/Alex4SSB/ADB-Explorer/security/advisories/GHSA-rg2h-2p33-rxcr
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27115.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-27115
- https://github.com/Alex4SSB/ADB-Explorer/commit/f7554690b1f68c6066c12aa45aec60303bca545b
