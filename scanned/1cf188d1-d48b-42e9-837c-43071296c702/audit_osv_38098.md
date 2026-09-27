# [C] Sandboxie-Plus local privilege escalation via TOCTOU race condition in UpdUtil addon installation

## Summary
Severity: Critical
Advisory: CVE-2026-34596
Aliases: GHSA-xjvp-63f2-v585
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/CVE-2026-34596
Type: osv

## Details
Sandboxie-Plus is an open source sandbox-based isolation software for Windows. In versions 1.17.2 and earlier, a Time-of-Check-to-Time-of-Use (TOCTOU) race condition exists during addon installation. When a user installs an addon through the SandMan interface, UpdUtil.exe is spawned as SYSTEM by SbieSvc but stages files in the user-writable %TEMP%\sandboxie-updater directory. After UpdUtil verifies file hashes against the signed addon manifest, install.bat extracts files.cab and executes config.exe from its contents. Between hash verification and extraction, an unprivileged user can replace files.cab with a crafted cabinet containing a malicious executable, which is then run as SYSTEM. No UAC prompt is required.

This issue has been fixed in version 1.17.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34596.json
- https://github.com/sandboxie-plus/Sandboxie/security/advisories/GHSA-xjvp-63f2-v585
- https://nvd.nist.gov/vuln/detail/CVE-2026-34596
