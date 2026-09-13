# [M] CVE-2023-23558

## Summary
Severity: Medium
Advisory: CVE-2023-23558
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-02-16
Source: https://osv.dev/vulnerability/CVE-2023-23558
Type: osv

## Details
In Eternal Terminal 6.2.1, TelemetryService uses fixed paths in /tmp. For example, a local attacker can create /tmp/.sentry-native-etserver with mode 0777 before the etserver process is started. The attacker can choose to read sensitive information from that file, or modify the information in that file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/23xxx/CVE-2023-23558.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-23558
- https://bugzilla.suse.com/show_bug.cgi?id=1207126
- https://github.com/MisterTea/EternalTerminal
- http://www.openwall.com/lists/oss-security/2023/02/16/1
