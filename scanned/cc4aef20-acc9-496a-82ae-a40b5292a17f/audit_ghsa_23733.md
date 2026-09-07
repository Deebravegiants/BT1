# [M] Cross-site Scripting in in JRuby

## Summary
Severity: Medium
Advisory: GHSA-wmq2-jc9m-xp4m
CVE: CVE-2010-1330
CWE: CWE-79
Ecosystem: Maven
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-wmq2-jc9m-xp4m
Type: github-advisory

## Affected
- Maven: `org.jruby:jruby-core` — affected >=0 <1.4.1

## Details
The regular expression engine in JRuby before 1.4.1, when $KCODE is set to 'u', does not properly handle characters immediately after a UTF-8 character, which allows remote attackers to conduct cross-site scripting (XSS) attacks via a crafted string.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-1330
- https://bugs.gentoo.org/show_bug.cgi?id=317435
- https://bugzilla.redhat.com/show_bug.cgi?id=750306
- https://exchange.xforce.ibmcloud.com/vulnerabilities/80277
- https://github.com/jruby/jruby
- http://rhn.redhat.com/errata/RHSA-2011-1456.html
- http://secunia.com/advisories/46891
- http://www.jruby.org/2010/04/26/jruby-1-4-1-xss-vulnerability.html
- http://www.osvdb.org/77297
