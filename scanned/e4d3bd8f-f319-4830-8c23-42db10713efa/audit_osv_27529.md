# [M] Incomplete disallowed remote addresses list in MyBB

## Summary
Severity: Medium
Advisory: CVE-2024-23336
Aliases: GHSA-qfrj-65mv-h75h
CVSS: 5.0 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-23336
Type: osv

## Details
MyBB is a free and open source forum software. The default list of disallowed remote hosts does not contain the `127.0.0.0/8` block, which may result in a Server-Side Request Forgery (SSRF) vulnerability. The Configuration File's _Disallowed Remote Addresses_ list (`$config['disallowed_remote_addresses']`) contains the address `127.0.0.1`, but does not include the complete block `127.0.0.0/8`. MyBB 1.8.38 resolves this issue in default installations. Administrators of installed boards should update the existing configuration (`inc/config.php`) to include all addresses blocked by default. Additionally, users are advised to verify that it includes any other IPv4 addresses resolving to the server and other internal resources. Users unable to upgrade may manually add 127.0.0.0/8' to their disallowed address list.

## References
- https://docs.mybb.com/1.8/administration/configuration-file
- https://mybb.com/versions/1.8.38
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/23xxx/CVE-2024-23336.json
- https://github.com/mybb/mybb/security/advisories/GHSA-qfrj-65mv-h75h
- https://nvd.nist.gov/vuln/detail/CVE-2024-23336
- https://github.com/mybb/mybb/commit/d6a96019025de9149014e06b1df252e6122e5630
