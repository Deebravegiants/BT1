# [H] pam_usb: PAM_RHOST check skipped when deny_remote=false allows XDMCP authentication bypass

## Summary
Severity: High
Advisory: CVE-2026-48064
Aliases: GHSA-w38v-cw9r-x9p6
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-48064
Type: osv

## Details
pam_usb provides hardware authentication for Linux using ordinary removable media. Prior to 0.9.1, when a PAM service is configured with deny_remote=false in pam_usb (commonly done for display managers such as gdm-password or lightdm to bypass process/TTY heuristics for local sessions), the PAM_RHOST check in pusb_do_auth() is also skipped. PAM_RHOST is set by remote daemons (sshd, XDMCP servers) to identify the remote client address. Because the check is gated inside if (opts.deny_remote), a genuine remote XDMCP connection reaches the USB device authentication step instead of being rejected. This vulnerability is fixed in 0.9.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48064.json
- https://github.com/mcdope/pam_usb/security/advisories/GHSA-w38v-cw9r-x9p6
- https://nvd.nist.gov/vuln/detail/CVE-2026-48064
- https://github.com/mcdope/pam_usb/issues/348
