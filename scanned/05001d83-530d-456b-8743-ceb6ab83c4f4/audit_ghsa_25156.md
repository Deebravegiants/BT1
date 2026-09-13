# [M] Roundup Improper Access Control

## Summary
Severity: Medium
Advisory: GHSA-9rj9-5wcv-xgf2
CVE: CVE-2009-2737
CWE: CWE-284
Ecosystem: PyPI
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-9rj9-5wcv-xgf2
Type: github-advisory

## Affected
- PyPI: `Roundup` — affected >=1.2 <1.2.1
- PyPI: `Roundup` — affected >=1.4 <1.4.7

## Details
The EditCSVAction function in `cgi/actions.py` in Roundup 1.2 before 1.2.1, 1.4 through 1.4.6, and possibly other versions does not properly check permissions, which allows remote authenticated users with edit or create privileges for a class to modify arbitrary items within that class, as demonstrated by editing all queries, modifying settings, and adding roles to users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-2737
- https://bugzilla.redhat.com/show_bug.cgi?id=489355
- https://github.com/roundup-tracker/roundup/blob/d24abceaa19072b28e5c8ae0db4dd341597d14fc/CHANGES.txt#L2356
- https://sourceforge.net/p/roundup/code/ci/4081
- https://www.redhat.com/archives/fedora-package-announce/2009-March/msg00429.html
- https://www.redhat.com/archives/fedora-package-announce/2009-March/msg00439.html
- http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=518768
- http://issues.roundup-tracker.org/issue2550521
- http://secunia.com/advisories/34192
- http://www.debian.org/security/2009/dsa-1754
- http://www.osvdb.org/56368
- http://www.securityfocus.com/bid/34059
