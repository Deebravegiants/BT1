# [H] pam_usb: Command injection via $TMUX environment variable leads to RCE as root

## Summary
Severity: High
Advisory: CVE-2026-44713
Aliases: GHSA-822m-whrh-vrj8
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-44713
Type: osv

## Details
pam_usb provides hardware authentication for Linux using ordinary removable media. Prior to 0.8.7, src/tmux.c reads the user's $TMUX environment variable, splits it on commas, and interpolates the socket-path component directly into a shell command passed to popen(). Because the value is placed inside double-quotes without sanitisation, any value containing " terminates the quoted string and injects arbitrary shell syntax. popen() runs as root inside the PAM stack. This vulnerability is fixed in 0.8.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44713.json
- https://github.com/mcdope/pam_usb/security/advisories/GHSA-822m-whrh-vrj8
- https://nvd.nist.gov/vuln/detail/CVE-2026-44713
