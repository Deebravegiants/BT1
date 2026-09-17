# [H] CVE-2026-48695

## Summary
Severity: High
Advisory: CVE-2026-48695
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-48695
Type: osv

## Details
FastNetMon Community Edition through 1.2.9 contains an OS command injection vulnerability in the MikroTik router integration plugin. The _log() function in src/mikrotik_plugin/fastnetmon_mikrotik.php (lines 107-108) constructs shell commands by concatenating the $msg parameter directly into exec() calls: exec("echo `date` \"- {FASTNETMON] - " . $msg . " \" >> " . $FILE_LOG_TMP). This is identical in pattern to the Juniper plugin vulnerability. The $msg variable contains unsanitized attack data from command-line arguments. An attacker who can influence argv[] values can inject arbitrary shell commands. The fix is to replace exec() with file_put_contents() or use escapeshellarg().

## References
- https://github.com/pavel-odintsov/fastnetmon/blob/master/src/mikrotik_plugin/fastnetmon_mikrotik.php
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48695.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-48695
- https://github.com/pavel-odintsov/fastnetmon
- https://lorikeetsecurity.com/blog/fastnetmon-cve-2026-48695-mikrotik-cmd-injection
