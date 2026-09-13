# [M] Ruby vulnerable to denial of service

## Summary
Severity: Medium
Advisory: GHSA-hgg7-cghq-xhf4
CVE: CVE-2013-1821
CWE: CWE-400
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-hgg7-cghq-xhf4
Type: github-advisory

## Affected
- Maven: `org.jruby:jruby` — affected >=0 <1.7.3

## Details
When reading text nodes from an XML document, the REXML parser can be coerced in to allocating extremely large string objects which can consume all of the memory on a machine, causing a denial of service.

Jruby resolves this bug in version 1.7.3 as noted in https://www.jruby.org/2013/02/21/jruby-1-7-3.html

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1821
- https://bugzilla.redhat.com/show_bug.cgi?id=914716
- https://github.com/jruby/jruby
- https://wiki.mageia.org/en/Support/Advisories/MGASA-2013-0092
- https://www.jruby.org/2013/02/21/jruby-1-7-3.html
- http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=702525
- http://lists.opensuse.org/opensuse-security-announce/2013-04/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2013-04/msg00015.html
- http://lists.opensuse.org/opensuse-updates/2013-04/msg00034.html
- http://lists.opensuse.org/opensuse-updates/2013-04/msg00036.html
- http://rhn.redhat.com/errata/RHSA-2013-1147.html
- http://svn.ruby-lang.org/cgi-bin/viewvc.cgi?view=revision&revision=39384
- http://www.debian.org/security/2013/dsa-2738
- http://www.debian.org/security/2013/dsa-2809
- http://www.mandriva.com/security/advisories?name=MDVSA-2013:124
- http://www.openwall.com/lists/oss-security/2013/03/06/5
- http://www.ruby-lang.org/en/news/2013/02/22/rexml-dos-2013-02-22
- http://www.slackware.com/security/viewer.php?l=slackware-security&y=2013&m=slackware-security.426862
- http://www.ubuntu.com/usn/USN-1780-1
