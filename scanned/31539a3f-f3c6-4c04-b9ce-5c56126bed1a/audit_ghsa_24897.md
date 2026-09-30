# [H] CherryPy Malicious cookies allow access to files outside the session directory

## Summary
Severity: High
Advisory: GHSA-76x8-gg39-5jjg
CVE: CVE-2008-0252
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-76x8-gg39-5jjg
Type: github-advisory

## Affected
- PyPI: `cherrypy` — affected >=0 <2.1.1
- PyPI: `cherrypy` — affected >=3.0 <3.0.2

## Details
Directory traversal vulnerability in the _get_file_path function in (1) `lib/sessions.py` in CherryPy 3.0.x up to 3.0.2, (2) `filter/sessionfilter.py` in CherryPy 2.1, and (3) `filter/sessionfilter.py` in CherryPy 2.x allows remote attackers to create or delete arbitrary files, and possibly read and write portions of arbitrary files, via a crafted session id in a cookie.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-0252
- https://github.com/cherrypy/cherrypy/commit/37b856eba6f207231c691dae2e5b24e072f86664
- https://bugs.gentoo.org/show_bug.cgi?id=204829
- https://github.com/cherrypy/cherrypy
- https://github.com/pypa/advisory-database/tree/main/vulns/cherrypy/PYSEC-2008-3.yaml
- https://issues.rpath.com/browse/RPL-2127
- https://web.archive.org/web/20080129011723/http://secunia.com/advisories/28354
- https://web.archive.org/web/20080312130713/http://secunia.com/advisories/28353
- https://web.archive.org/web/20080328003510/http://secunia.com/advisories/28611
- https://web.archive.org/web/20100122080212/http://www.vupen.com/english/advisories/2008/0039
- https://web.archive.org/web/20110513223620/http://secunia.com/advisories/28769
- https://web.archive.org/web/20111224161644/http://secunia.com/advisories/28620
- https://web.archive.org/web/20151108024505/http://www.securityfocus.com/bid/27181
- https://www.redhat.com/archives/fedora-package-announce/2008-January/msg00240.html
- https://www.redhat.com/archives/fedora-package-announce/2008-January/msg00297.html
- http://security.gentoo.org/glsa/glsa-200801-11.xml
- http://www.cherrypy.org/changeset/1774
- http://www.cherrypy.org/changeset/1775
- http://www.cherrypy.org/changeset/1776
- http://www.cherrypy.org/ticket/744
