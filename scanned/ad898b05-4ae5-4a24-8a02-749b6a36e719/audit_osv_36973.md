# [C] ADB-Explorer: UNC Path Support in ManualAdbPath Leads to Remote Code Execution (RCE)

## Summary
Severity: Critical
Advisory: CVE-2026-27615
Aliases: GHSA-3f27-jp2g-hwhr
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-27615
Type: osv

## Details
ADB Explorer is a fluent UI for ADB on Windows. In versions prior to Beta 0.9.26022, ADB-Explorer allows the `ManualAdbPath` settings variable, which determines the path of the ADB binary to be executed, to be set to a Universal Naming Convention (UNC) path in the application's settings file. This allows an attacker to set the binary's path to point to a remote network resource, hosted on an attacker-controlled network share, thus granting the attacker full control over the binary being executed by the app. An attacker may leverage this vulnerability to execute code remotely on a victim's machine with the privileges of the user running the app. Exploitation is made possible by convincing a victim to run a shortcut of the app that points to a custom `App.txt` settings file, which sets `ManualAdbPath` (for example, when downloaded in an archive file). Version Beta 0.9.26022 fixes the issue.

## References
- https://github.com/Alex4SSB/ADB-Explorer/security/advisories/GHSA-3f27-jp2g-hwhr
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27615.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-27615
