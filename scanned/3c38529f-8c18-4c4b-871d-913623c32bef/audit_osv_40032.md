# [M] pam_usb: Infinite loop DoS in process-tree walk when parent process exits during authentication

## Summary
Severity: Medium
Advisory: CVE-2026-48986
Aliases: GHSA-h28h-9hc3-v595
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2026-48986
Type: osv

## Details
pam_usb provides hardware authentication for Linux using removable media. In pam_usb 0.9.1 and earlier, usb_get_process_parent_id() can cause an infinite loop DoS because it does not initialize *ppid on failure. In pusb_local_login(), the same variable is reused as input and output in a process-tree while loop; if /proc/<pid>/stat cannot be read (for example, when an ancestor process exits during authentication), the PID is not updated and the loop does not terminate. This hangs the authenticating process (such as sudo, sshd, or login) until it is forcibly terminated. This issue has been fixed in version 0.9.2.

## References
- https://github.com/mcdope/pam_usb/releases/tag/0.9.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48986.json
- https://github.com/mcdope/pam_usb/security/advisories/GHSA-h28h-9hc3-v595
- https://nvd.nist.gov/vuln/detail/CVE-2026-48986
