# [H] Path Traversal and Denial of Service in parisneo/lollms-webui

## Summary
Severity: High
Advisory: CVE-2024-1873
CVSS: 8.2 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L)
Published: 2024-06-06
Source: https://osv.dev/vulnerability/CVE-2024-1873
Type: osv

## Details
parisneo/lollms-webui is vulnerable to path traversal and denial of service attacks due to an exposed `/select_database` endpoint in version a9d16b0. The endpoint improperly handles file paths, allowing attackers to specify absolute paths when interacting with the `DiscussionsDB` instance. This flaw enables attackers to create directories anywhere on the system where the application has permissions, potentially leading to denial of service by creating directories with names of critical files, such as HTTPS certificate files, causing server startup failures. Additionally, attackers can manipulate the database path, resulting in the loss of client data by constantly changing the file location to an attacker-controlled location, scattering the data across the filesystem and making recovery difficult.

## References
- https://huntr.com/bounties/c1cfc0d9-517a-4d0e-bf1c-6444c1fd195d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/1xxx/CVE-2024-1873.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-1873
- https://github.com/parisneo/lollms-webui/commit/02e829b5653a1aa5dbbe9413ec84f96caa1274e8
