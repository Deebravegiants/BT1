# [M] pam_usb: xfree() does not call explicit_bzero — sensitive cryptographic material may linger in freed heap

## Summary
Severity: Medium
Advisory: CVE-2026-48984
Aliases: GHSA-rmp6-wfrq-wrrc
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2026-48984
Type: osv

## Details
pam_usb provides hardware authentication for Linux using ordinary removable media. In versions 0.9.1 and below, the xfree() memory release helper in calls free() without first zeroing the buffer contents, releasing heap-allocated buffers containing sensitive data — including one-time pad bytes read from disk — without clearing, leaving the sensitive content in freed heap memory until it happens to be overwritten by a subsequent allocation. On a system where a use-after-free condition exists, or where a heap inspection primitive becomes available, this could allow recovery of pad values or other authentication material from freed memory regions. This is a defence-in-depth requirement consistent with prior hardening work in this codebase (GHSA-vx6f-rrqr-j87c applied explicit_bzero to some pad paths; this issue generalises the pattern to the central deallocation helper).

## References
- https://github.com/mcdope/pam_usb/releases/tag/0.9.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48984.json
- https://github.com/mcdope/pam_usb/security/advisories/GHSA-rmp6-wfrq-wrrc
- https://nvd.nist.gov/vuln/detail/CVE-2026-48984
