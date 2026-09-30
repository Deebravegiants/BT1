# [M] Nextcloud Server and Groupfolders app vulnerable to bypass of group folder quota limit using attachment in text file

## Summary
Severity: Medium
Advisory: CVE-2025-47793
Aliases: GHSA-qqgg-hhfq-vhww
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2025-05-16
Source: https://osv.dev/vulnerability/CVE-2025-47793
Type: osv

## Details
Nextcloud Server is a self hosted personal cloud system, and the Nextcloud Groupfolders app provides admin-configured folders shared by everyone in a group or team. In Nextcloud Server prior to 30.0.2, 29.0.9, and 28.0.1, Nextcloud Enterprise Server prior to 30.0.2 and 29.0.9, and Nextcloud Groupfolders app prior to 18.0.3, 17.0.5, and 16.0.11, the absence of quota checking on attachments allowed logged-in users to upload files exceeding the group folder quota. Nextcloud Server versions 30.0.2 and 29.0.9, Nextcloud Enterprise Server versions 30.0.2, 29.0.9, or 28.0.12, and Nextcloud Groupfolders app 18.0.3, 17.0.5, and 16.0.11 fix the issue. No known workarounds are available.

## References
- https://hackerone.com/reports/2713272
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/47xxx/CVE-2025-47793.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-qqgg-hhfq-vhww
- https://nvd.nist.gov/vuln/detail/CVE-2025-47793
- https://github.com/nextcloud/groupfolders/pull/3328
- https://github.com/nextcloud/server/pull/48623
