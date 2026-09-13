# [M] pam_usb: Thread-unsafe static pointer in log.c causes data race under concurrent PAM authentication

## Summary
Severity: Medium
Advisory: CVE-2026-48066
Aliases: GHSA-qg76-57wq-mpv6
CVSS: 5.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-48066
Type: osv

## Details
pam_usb provides hardware authentication for Linux using ordinary removable media. Prior to 0.9.1, src/log.c contains a process-wide static pointer that is written on every PAM invocation with the address of a stack-local variable. This violates the PAM re-entrancy requirement and creates a data race when the PAM stack is invoked concurrently from multiple threads. This vulnerability is fixed in 0.9.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48066.json
- https://github.com/mcdope/pam_usb/security/advisories/GHSA-qg76-57wq-mpv6
- https://nvd.nist.gov/vuln/detail/CVE-2026-48066
- https://github.com/mcdope/pam_usb/issues/350
- https://github.com/mcdope/pam_usb/issues/55
