# [M] xrdp: Authenticated RCE via unsanitized AlternateShell execution in xrdp-sesman

## Summary
Severity: Medium
Advisory: CVE-2026-33145
Aliases: GHSA-rmvv-7633-fg7h
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-33145
Type: osv

## Details
xrdp is an open source RDP server. Versions through 0.10.5 allow an authenticated remote user to execute arbitrary commands on the server due to unsafe handling of the AlternateShell parameter in xrdp-sesman. When the AllowAlternateShell setting is enabled (which is the default when not explicitly configured), xrdp accepts a client-supplied AlternateShell value and executes it via /bin/sh -c during session initialization. This results in shell-interpreted execution of unsanitized, user-controlled input. This behavior effectively provides a scriptable remote command execution primitive over RDP within the security context of the authenticated user, occurring prior to normal window manager startup. This can bypass expected session initialization flows and operational assumptions that restrict execution to interactive desktop environments. This issue has been fixed in version 0.10.6.

## References
- https://github.com/neutrinolabs/xrdp/releases/tag/v0.10.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33145.json
- https://github.com/neutrinolabs/xrdp/security/advisories/GHSA-rmvv-7633-fg7h
- https://nvd.nist.gov/vuln/detail/CVE-2026-33145
