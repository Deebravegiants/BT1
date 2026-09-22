# [C] JGit Improper Input Validation vulnerability

## Summary
Severity: Critical
Advisory: GHSA-6vvc-c2m3-cjf3
CVE: CVE-2014-9390
CWE: CWE-20
Ecosystem: Maven, PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-6vvc-c2m3-cjf3
Type: github-advisory

## Affected
- Maven: `org.eclipse.jgit:org.eclipse.jgit` — affected >=0 <3.5.3
- PyPI: `mercurial` — affected >=0 <3.2.3

## Details
Git before 1.8.5.6, 1.9.x before 1.9.5, 2.0.x before 2.0.5, 2.1.x before 2.1.4, and 2.2.x before 2.2.1 on Windows and OS X; Mercurial before 3.2.3 on Windows and OS X; Apple Xcode before 6.2 beta 3; mine; libgit2; Egit; and JGit allow remote Git servers to execute arbitrary commands via a tree containing a crafted .git/config file with (1) an ignorable Unicode codepoint, (2) a git~1/config representation, or (3) mixed case that is improperly handled on a case-insensitive filesystem.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-9390
- https://github.com/libgit2/libgit2/commit/928429c5c96a701bcbcafacb2421a82602b36915
- https://github.com/blog/1938-git-client-vulnerability-announced
- https://github.com/pypa/advisory-database/tree/main/vulns/mercurial/PYSEC-2020-217.yaml
- https://libgit2.org/security
- https://news.ycombinator.com/item?id=8769667
- https://projects.eclipse.org/projects/technology.jgit/releases/3.5.3
- https://web.archive.org/web/20211204220400/https://securitytracker.com/id?1031404
- http://article.gmane.org/gmane.linux.kernel/1853266
- http://git-blame.blogspot.com/2014/12/git-1856-195-205-214-and-221-and.html
- http://mercurial.selenic.com/wiki/WhatsNew
- http://securitytracker.com/id?1031404
- http://support.apple.com/kb/HT204147
