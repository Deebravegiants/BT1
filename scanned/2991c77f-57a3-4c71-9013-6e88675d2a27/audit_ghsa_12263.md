# [M] gtk2 vulnerable to Use of Externally-Controlled Format String

## Summary
Severity: Medium
Advisory: GHSA-xgj6-pgrm-x4r2
CVE: CVE-2007-6183
CWE: CWE-134
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-xgj6-pgrm-x4r2
Type: github-advisory

## Affected
- RubyGems: `gtk2` — affected >=0 <0.17.0

## Details
Format string vulnerability in the `mdiag_initialize` function in `gtk/src/rbgtkmessagedialog.c` in Ruby-GNOME 2 (aka Ruby/Gnome2) 0.16.0, and SVN versions before 20071127, allows context-dependent attackers to execute arbitrary code via format string specifiers in the message parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2007-6183
- https://bugzilla.redhat.com/show_bug.cgi?id=402871
- https://exchange.xforce.ibmcloud.com/vulnerabilities/38757
- https://web.archive.org/web/20200228174159/http://www.securityfocus.com/bid/26616
- https://web.archive.org/web/20201207224244/https://www.securityfocus.com/archive/1/484240/100/0/threaded
- https://www.redhat.com/archives/fedora-package-announce/2007-December/msg00214.html
- https://www.redhat.com/archives/fedora-package-announce/2007-December/msg00251.html
- http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=453689
- http://bugs.gentoo.org/show_bug.cgi?id=200623
- http://em386.blogspot.com/2007/11/your-favorite-better-than-c-scripting.html
- http://security.gentoo.org/glsa/glsa-200712-09.xml
- http://securityreason.com/securityalert/3407
- http://www.debian.org/security/2007/dsa-1431
- http://www.mandriva.com/en/support/security/advisories/advisory/MDVSA-2008:033/?name=MDVSA-2008:033
