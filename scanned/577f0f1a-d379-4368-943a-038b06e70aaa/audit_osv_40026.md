# [M] pam_usb: getenv() used in PAM context allows environment variable injection into local-check logic

## Summary
Severity: Medium
Advisory: CVE-2026-48980
Aliases: GHSA-qr83-mf3h-fvqr
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2026-48980
Type: osv

## Details
pam_usb provides hardware authentication for Linux using removable media. In versions prior to 0.9.2,  getenv() environment variables XRDP_SESSION, DISPLAY and TMUX allow environment variable injection into local-check logic. These environment variables influence whether a current session is local or remote, and a PAM module that runs in the context of setuid binaries (sudo, su), getenv() returns attacker-controlled values whenever the process environment has been manipulated by a local user. This issue has been fixed in version 0.9.2.

## References
- https://github.com/mcdope/pam_usb/releases/tag/0.9.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48980.json
- https://github.com/mcdope/pam_usb/security/advisories/GHSA-qr83-mf3h-fvqr
- https://nvd.nist.gov/vuln/detail/CVE-2026-48980
