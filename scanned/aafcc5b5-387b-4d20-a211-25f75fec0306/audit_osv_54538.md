# [M] CVE-2024-0911

## Summary
Severity: Medium
Advisory: CVE-2024-0911
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-06
Source: https://osv.dev/vulnerability/CVE-2024-0911
Type: osv

## Details
A flaw was found in indent, a program for formatting C code. This issue may allow an attacker to trick a user into processing a specially crafted file to trigger a heap-based buffer overflow, causing the application to crash.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AYVDWBSJROWOWMPDVMVG4L5FGVJC5REN/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GIEHMOQDLPRTE4FDOA4X6PMOCNLK6BCP/
- https://lists.gnu.org/archive/html/bug-indent/2024-01/msg00000.html
- https://access.redhat.com/security/cve/CVE-2024-0911
- https://bugzilla.redhat.com/show_bug.cgi?id=2260399
