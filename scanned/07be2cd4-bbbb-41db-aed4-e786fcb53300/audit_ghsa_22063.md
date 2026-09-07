# [M] Mako contains Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7q8x-38mc-p84f
CVE: CVE-2010-2480
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-7q8x-38mc-p84f
Type: github-advisory

## Affected
- PyPI: `mako` — affected >=0 <0.3.4

## Details
Mako before 0.3.4 relies on the cgi.escape function in the Python standard library for cross-site scripting (XSS) protection, which makes it easier for remote attackers to conduct XSS attacks via vectors involving single-quote characters and a JavaScript onLoad event handler for a BODY element.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-2480
- https://access.redhat.com/security/cve/CVE-2010-2480
- https://bugs.python.org/issue9061
- https://bugzilla.redhat.com/show_bug.cgi?id=609573
- https://github.com/pypa/advisory-database/tree/main/vulns/mako/PYSEC-2010-1.yaml
- https://github.com/sqlalchemy/mako
- https://lists.opensuse.org/opensuse-security-announce/2010-08/msg00001.html
- https://www.makotemplates.org/CHANGES
- http://bugs.python.org/issue9061
- http://lists.opensuse.org/opensuse-security-announce/2010-08/msg00001.html
- http://www.makotemplates.org/CHANGES
