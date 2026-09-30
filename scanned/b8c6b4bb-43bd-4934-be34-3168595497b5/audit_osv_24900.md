# [M] Denial of Service while unescaping a Markdown string

## Summary
Severity: Medium
Advisory: CVE-2023-2831
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-06-16
Source: https://osv.dev/vulnerability/CVE-2023-2831
Type: osv

## Details
Mattermost fails to unescape Markdown strings in a memory-efficient way, allowing an attacker to cause a Denial of Service by sending a message containing a large number of escaped characters.

## References
- https://mattermost.com/security-updates/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2831.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-2831
