# [M] pam_usb: TOCTOU race condition in pad directory creation allows symlink substitution

## Summary
Severity: Medium
Advisory: CVE-2026-48983
Aliases: GHSA-4j8q-67fq-3xc3
CVSS: 5.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:L)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2026-48983
Type: osv

## Details
pam_usb provides hardware authentication for Linux using ordinary removable media. In versions prior to 0.9.2, a symlink race condition exists in per-device and per-user pad directory creation. pam_usb uses a check-then-act pattern: it calls lstat() to test for existence and then calls mkdir() separately to create the directory. A local attacker can win the race between these calls by replacing the target path with a symlink to a directory they control. If successful, one-time pad files may be written to an attacker-controlled location, potentially exposing future pad values before use or disrupting authentication. This issue has been fixed in version 0.9.2.

## References
- https://github.com/mcdope/pam_usb/releases/tag/0.9.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48983.json
- https://github.com/mcdope/pam_usb/security/advisories/GHSA-4j8q-67fq-3xc3
- https://nvd.nist.gov/vuln/detail/CVE-2026-48983
