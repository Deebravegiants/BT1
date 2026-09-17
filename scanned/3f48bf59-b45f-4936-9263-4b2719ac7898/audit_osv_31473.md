# [H] Emacs: shell injection vulnerability in gnu emacs via custom "man" uri scheme

## Summary
Severity: High
Advisory: CVE-2025-1244
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-02-12
Source: https://osv.dev/vulnerability/CVE-2025-1244
Type: osv

## Details
A command injection flaw was found in the text editor Emacs. It could allow a remote, unauthenticated attacker to execute arbitrary shell commands on a vulnerable system. Exploitation is possible by tricking users into visiting a specially crafted website or an HTTP URL with a redirect.

## References
- http://www.openwall.com/lists/oss-security/2025/03/01/2
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://debbugs.gnu.org/cgi/bugreport.cgi?bug=66390
- https://git.savannah.gnu.org/cgit/emacs.git/
- https://git.savannah.gnu.org/cgit/emacs.git/commit/?id=820f0793f0b46448928905552726c1f1b999062f
- https://git.savannah.gnu.org/cgit/emacs.git/tree/etc/NEWS?h=emacs-30.1
- https://lists.debian.org/debian-lts-announce/2025/02/msg00033.html
- https://access.redhat.com/errata/RHSA-2025:1915
- https://access.redhat.com/errata/RHSA-2025:1917
- https://access.redhat.com/errata/RHSA-2025:1961
- https://access.redhat.com/errata/RHSA-2025:1962
- https://access.redhat.com/errata/RHSA-2025:1963
- https://access.redhat.com/errata/RHSA-2025:1964
- https://access.redhat.com/errata/RHSA-2025:2022
- https://access.redhat.com/errata/RHSA-2025:2130
- https://access.redhat.com/errata/RHSA-2025:2157
- https://access.redhat.com/errata/RHSA-2025:2195
- https://access.redhat.com/errata/RHSA-2025:2754
- https://access.redhat.com/security/cve/CVE-2025-1244
