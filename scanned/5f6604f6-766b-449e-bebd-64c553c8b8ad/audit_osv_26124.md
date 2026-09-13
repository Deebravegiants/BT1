# [H] Glibc: dos due to memory leak in getaddrinfo.c

## Summary
Severity: High
Advisory: CVE-2023-5156
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-09-25
Source: https://osv.dev/vulnerability/CVE-2023-5156
Type: osv

## Details
A flaw was found in the GNU C Library. A recent fix for CVE-2023-4806 introduced the potential for a memory leak, which may result in an application crash.

## References
- http://www.openwall.com/lists/oss-security/2023/10/03/4
- http://www.openwall.com/lists/oss-security/2023/10/03/5
- http://www.openwall.com/lists/oss-security/2023/10/03/6
- http://www.openwall.com/lists/oss-security/2023/10/03/8
- https://access.redhat.com/downloads/content/package-browser/
- https://sourceware.org/git/?p=glibc.git;a=commitdiff;h=ec6b95c3303c700eb89eebeda2d7264cc184a796
- https://access.redhat.com/security/cve/CVE-2023-5156
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/5xxx/CVE-2023-5156.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-5156
- https://security.gentoo.org/glsa/202402-01
- https://bugzilla.redhat.com/show_bug.cgi?id=2240541
- https://sourceware.org/bugzilla/show_bug.cgi?id=30884
