# [H] indirect remote shell command injection via unsanitized DHCP options in wicked

## Summary
Severity: High
Advisory: CVE-2026-44932
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-16
Source: https://osv.dev/vulnerability/CVE-2026-44932
Type: osv

## Details
Passing of unsanitized strings from DHCP replies into the wicked dhcp client before wicked 0.6.79 could be used by attackers operating a malicious DHCP server to execute code on the local machine.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44932.json
- https://github.com/openSUSE/wicked/releases/tag/version-0.6.79
- https://lists.suse.com/pipermail/sle-security-updates/2026-June/026688.html
- https://lists.suse.com/pipermail/sle-security-updates/2026-June/026689.html
- https://lists.suse.com/pipermail/sle-security-updates/2026-June/026690.html
- https://lists.suse.com/pipermail/sle-security-updates/2026-June/026691.html
- https://nvd.nist.gov/vuln/detail/CVE-2026-44932
- https://bugzilla.suse.com/show_bug.cgi?id=1265221
- https://github.com/openSUSE/wicked
