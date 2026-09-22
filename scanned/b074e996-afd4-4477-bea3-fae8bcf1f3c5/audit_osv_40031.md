# [M] pam_usb: NULL Dereference Crash in pusb_is_loginctl_local when loginctl Returns Empty Remote Field

## Summary
Severity: Medium
Advisory: CVE-2026-48985
Aliases: GHSA-7j6h-wfc2-mg5q
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2026-48985
Type: osv

## Details
pam_usb provides hardware authentication for Linux using ordinary removable media. In versions 0.9.1 and below, pusb_is_loginctl_local() can cause a NULL dereference crash when parsing loginctl output. The function calls popen() and reads the result; if the Remote field is only a newline, fgets() succeeds but strtok_r(buf, "\n", &saveptr) returns NULL. A subsequent strcmp(is_remote, "no") then dereferences NULL, causing undefined behavior (typically SIGSEGV) and crashing the PAM module. This can crash the authenticating process (e.g., sudo, login) and, depending on PAM stack configuration, deny access for all users of the affected service. This issue has been fixed in version 0.9.2.

## References
- https://github.com/mcdope/pam_usb/releases/tag/0.9.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48985.json
- https://github.com/mcdope/pam_usb/security/advisories/GHSA-7j6h-wfc2-mg5q
- https://nvd.nist.gov/vuln/detail/CVE-2026-48985
