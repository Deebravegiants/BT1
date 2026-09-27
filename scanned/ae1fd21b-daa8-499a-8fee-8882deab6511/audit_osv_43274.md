# [M] Vim: Stack Buffer Overflow in the Vim Socket Server

## Summary
Severity: Medium
Advisory: CVE-2026-73070
Aliases: GHSA-49m8-wwxj-mr69
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73070
Type: osv

## Details
Vim is an open source, command line text editor. Prior to 9.2.0842, the socket server backend in src/socketserver.c accepts unbounded client connections in socketserver_accept(), causing descriptors to overflow fd_set structures in src/channel.c and fixed-size struct pollfd arrays in src/os_unix.c, which allows a local process that can connect to the server socket to corrupt stack memory or terminate the Vim server. This issue is fixed in version 9.2.0842.

## References
- https://github.com/vim/vim/releases/tag/v9.2.0842
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73070.json
- https://github.com/vim/vim/security/advisories/GHSA-49m8-wwxj-mr69
- https://nvd.nist.gov/vuln/detail/CVE-2026-73070
- https://github.com/vim/vim/commit/5598618b2daf8e36b3bf0251caaefcf0bf8e85e4
