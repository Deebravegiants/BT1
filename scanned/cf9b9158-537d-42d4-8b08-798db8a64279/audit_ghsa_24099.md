# [C] Roundup xml-rpc server improper check of property permissions

## Summary
Severity: Critical
Advisory: GHSA-j59j-h3g7-cpmf
CVE: CVE-2008-1475
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-j59j-h3g7-cpmf
Type: github-advisory

## Affected
- PyPI: `roundup` — affected >=0 <1.4.5

## Details
The xml-rpc server in Roundup 1.4.4 does not check property permissions, which allows attackers to bypass restrictions and edit or read restricted properties via the (1) list, (2) display, and (3) set methods.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-1475
- https://github.com/roundup-tracker/roundup/commit/c00b7e5801f8baa246fa76b4aad5287882310189
- https://bugzilla.redhat.com/show_bug.cgi?id=436546
- https://exchange.xforce.ibmcloud.com/vulnerabilities/41240
- https://github.com/pypa/advisory-database/tree/main/vulns/roundup/PYSEC-2008-10.yaml
- https://github.com/roundup-tracker/roundup
- http://security.gentoo.org/glsa/glsa-200805-21.xml
- http://sourceforge.net/tracker/index.php?func=detail&aid=1907211&group_id=31577&atid=402788
- http://www.redhat.com/archives/fedora-package-announce/2008-March/msg00264.html
- http://www.redhat.com/archives/fedora-package-announce/2008-March/msg00375.html
- http://www.redhat.com/archives/fedora-package-announce/2008-November/msg00452.html
- http://www.redhat.com/archives/fedora-package-announce/2008-November/msg00478.html
