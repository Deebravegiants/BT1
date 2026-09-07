# [C] Mercurial vulnerable to arbitrary command execution via a crafted repository name in a clone command

## Summary
Severity: Critical
Advisory: GHSA-3pmw-h7j4-rf54
CVE: CVE-2014-9462
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-3pmw-h7j4-rf54
Type: github-advisory

## Affected
- PyPI: `mercurial` — affected >=0 <3.2.4

## Details
The _validaterepo function in sshpeer in Mercurial before 3.2.4 allows remote attackers to execute arbitrary commands via a crafted repository name in a clone command.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-9462
- https://github.com/pypa/advisory-database/tree/main/vulns/mercurial/PYSEC-2015-14.yaml
- https://security.gentoo.org/glsa/201612-19
- http://chargen.matasano.com/chargen/2015/3/17/this-new-vulnerability-mercurial-command-injection-cve-2014-9462.html
- http://lists.opensuse.org/opensuse-updates/2015-03/msg00085.html
- http://mercurial.selenic.com/wiki/WhatsNew
- http://www.debian.org/security/2015/dsa-3257
- http://www.oracle.com/technetwork/topics/security/bulletinjul2015-2511963.html
