# [H] CVE-2026-48687

## Summary
Severity: High
Advisory: CVE-2026-48687
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-48687
Type: osv

## Details
FastNetMon Community Edition through 1.2.9 contains an OS command injection vulnerability in the Juniper router integration plugin. The _log() function in src/juniper_plugin/fastnetmon_juniper.php (lines 117-118) constructs shell commands by concatenating the $msg parameter directly into exec() calls: exec("echo `date` \"- {FASTNETMON] - " . $msg . " \" >> " . $FILE_LOG_TMP). The $msg variable contains unsanitized data derived from command-line arguments argv[1] through argv[3], which represent the attack IP address, direction, and power. While FastNetMon's C++ core currently passes IP addresses via inet_ntoa() (which only produces safe dotted-decimal notation), the PHP script performs no input validation or shell escaping. If the script is invoked directly, by another orchestration system, or if future code changes pass string-sourced IPs, arbitrary commands can be injected. The correct fix is to replace exec() with file_put_contents() or use escapeshellarg() on all parameters.

## References
- https://github.com/pavel-odintsov/fastnetmon/blob/master/src/juniper_plugin/fastnetmon_juniper.php
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48687.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-48687
- https://github.com/pavel-odintsov/fastnetmon
- https://lorikeetsecurity.com/blog/fastnetmon-cve-2026-48687-juniper-cmd-injection
