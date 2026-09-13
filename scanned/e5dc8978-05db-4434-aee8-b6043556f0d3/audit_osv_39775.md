# [M] pam_usb: Uncontrolled search path in pam_usb tools allows privilege escalation via PATH manipulation

## Summary
Severity: Medium
Advisory: CVE-2026-47274
Aliases: GHSA-pp29-w28g-r9h9
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-47274
Type: osv

## Details
pam_usb provides hardware authentication for Linux using ordinary removable media. Prior to 0.9.0, multiple pam_usb helper tools resolved external binaries through the PATH environment variable rather than using absolute paths. An attacker who can influence the process environment during PAM authentication or tool execution could substitute malicious binaries. The affected tools are pamusb-check (src/tmux.c), pamusb-conf (tools/pamusb-conf), and pamusb-keyring-unlock-gnome (tools/pamusb-keyring-unlock-gnome). This vulnerability is fixed in 0.9.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47274.json
- https://github.com/mcdope/pam_usb/security/advisories/GHSA-pp29-w28g-r9h9
- https://nvd.nist.gov/vuln/detail/CVE-2026-47274
- https://github.com/mcdope/pam_usb/commit/1ee8745920388df48d001a8e61ba629071557937
- https://github.com/mcdope/pam_usb/commit/52a1fd6413b7ffcc1a5b58ce432be42e7bf0dbd0
- https://github.com/mcdope/pam_usb/commit/993e73d8bebb1d8e62677388de3402b6ec36b600
