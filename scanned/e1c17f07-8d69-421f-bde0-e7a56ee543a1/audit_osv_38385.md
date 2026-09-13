# [M] MaxKB: SSRF via sandbox network hook bypass

## Summary
Severity: Medium
Advisory: CVE-2026-39418
Aliases: GHSA-w9g4-q3gm-6q6w
CVSS: 5.0 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-04-14
Source: https://osv.dev/vulnerability/CVE-2026-39418
Type: osv

## Details
MaxKB is an open-source AI assistant for enterprise. In versions 2.7.1 and below, sandbox network protection can be bypassed by using socket.sendto() with the MSG_FASTOPEN flag. This allows authenticated user with tool-editing permissions to reach internal services that are explicitly blocked by the sandbox's banned hosts configuration. MaxKB's sandbox uses LD_PRELOAD to hook the connect() function and block connections to banned IPs, but Linux's sendto() with the MSG_FASTOPEN flag can establish TCP connections directly through the kernel without ever calling connect(), completely bypassing the IP validation. Although sendto is listed in the syscall() wrapper, this is ineffective because glibc invokes the kernel syscall directly rather than routing through the hooked syscall() function. This issue has been fixed in version 2.8.0.

## References
- https://github.com/1Panel-dev/MaxKB/releases/tag/v2.8.0
- https://github.com/1Panel-dev/MaxKB/security/advisories/GHSA-w9g4-q3gm-6q6w
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39418.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-39418
- https://github.com/1Panel-dev/MaxKB/commit/4d06362750b15390437f1d2e4d14ec79baef8559
