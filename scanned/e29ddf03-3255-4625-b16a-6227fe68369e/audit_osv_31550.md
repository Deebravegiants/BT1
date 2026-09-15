# [M] Dropbear: privilege escalation via unix domain socket forwardings

## Summary
Severity: Medium
Advisory: CVE-2025-14282
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-02-12
Source: https://osv.dev/vulnerability/CVE-2025-14282
Type: osv

## Details
A flaw was found in Dropbear. When running in multi-user mode and authenticating users, the dropbear ssh server does the socket forwardings requested by the remote client as root,
only switching to the logged-in user upon spawning a shell or performing
some operations like reading the user's files.
With the recent ability of also using unix domain sockets as the forwarding destination any user able to log in via ssh can connect to any unix socket with the root's credentials, bypassing both file system restrictions and any SO_PEERCRED / SO_PASSCRED checks performed by the peer.

## References
- http://www.openwall.com/lists/oss-security/2025/12/16/4
- http://www.openwall.com/lists/oss-security/2025/12/17/1
- https://github.com/mkj/dropbear/
- https://lists.ucc.gu.uwa.edu.au/pipermail/dropbear/2025q4/002390.html
- https://access.redhat.com/security/cve/CVE-2025-14282
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/14xxx/CVE-2025-14282.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-14282
- https://bugzilla.redhat.com/show_bug.cgi?id=2420052
- https://github.com/mkj/dropbear/pull/391
- https://github.com/mkj/dropbear/pull/394
