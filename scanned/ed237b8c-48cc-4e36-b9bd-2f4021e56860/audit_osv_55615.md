# [M] CVE-2026-1757

## Summary
Severity: Medium
Advisory: CVE-2026-1757
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-02-02
Source: https://osv.dev/vulnerability/CVE-2026-1757
Type: osv

## Details
A flaw was identified in the interactive shell of the xmllint utility, part of the libxml2 project, where memory allocated for user input is not properly released under certain conditions. When a user submits input consisting only of whitespace, the program skips command execution but fails to free the allocated buffer. Repeating this action causes memory to continuously accumulate. Over time, this can exhaust system memory and terminate the xmllint process, creating a denial-of-service condition on the local system.

## References
- https://access.redhat.com/security/cve/CVE-2026-1757
- https://bugzilla.redhat.com/show_bug.cgi?id=2435940
- https://gitlab.gnome.org/GNOME/libxml2/-/issues/1009
