# [C] Local Privilege Escalation in Sparkle Autoupdate Daemon

## Summary
Severity: Critical
Advisory: CVE-2025-10016
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2025-10016
Type: osv

## Details
The Sparkle framework includes a helper tool Autoupdate. Due to lack of authentication of connecting clients a local unprivileged attacker  can request installation of crafted malicious PKG file by racing to connect to the daemon when other app spawns it as root. This results in local privilege escalation to root privileges. It is worth noting that it is possible to spawn Autopudate manually via Installer XPC service. However this requires the victim to enter credentials upon system authorization dialog creation that can be modified by the attacker.

This issue was fixed in version 2.7.2

## References
- https://cert.pl/en/posts/2025/09/CVE-2025-10015
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/10xxx/CVE-2025-10016.json
- https://github.com/sparkle-project/Sparkle/discussions/2764
- https://nvd.nist.gov/vuln/detail/CVE-2025-10016
- https://github.com/sparkle-project/Sparkle
