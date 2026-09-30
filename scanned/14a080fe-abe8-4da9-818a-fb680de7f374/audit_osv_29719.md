# [H] CVE-2024-45752

## Summary
Severity: High
Advisory: CVE-2024-45752
CVSS: 8.5 (CVSS:3.1/AC:L/AV:L/A:L/C:H/I:H/PR:N/S:C/UI:R)
Published: 2024-09-19
Source: https://osv.dev/vulnerability/CVE-2024-45752
Type: osv

## Details
logiops through 0.3.4, in its default configuration, allows any unprivileged user to configure its logid daemon via an unrestricted D-Bus service, including setting malicious keyboard macros. This allows for privilege escalation with minimal user interaction.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45752.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-45752
- https://bugzilla.suse.com/show_bug.cgi?id=1226598
- https://github.com/PixlOne/logiops/releases
