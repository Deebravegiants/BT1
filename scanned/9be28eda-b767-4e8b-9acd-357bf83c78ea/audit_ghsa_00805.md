# [C] Heap Based Buffer Overflow in libyaml

## Summary
Severity: Critical
Advisory: GHSA-m75h-cghq-c8h5
CVE: CVE-2013-6393
CWE: CWE-119
Ecosystem: npm
Published: 2020-08-31
Source: https://github.com/advisories/GHSA-m75h-cghq-c8h5
Type: github-advisory

## Affected
- npm: `libyaml` — affected >=0 <0.2.3

## Details
Versions 0.2.2 and earlier depend on native libyaml version 0.1.5 or earlier. As such, they are affected by a heap-based buffer overflow vulnerability that may result in a crash or arbitrary code execution when parsing YAML tags.





## Recommendation

- Update to version 0.2.3 that includes a version of LibYAML that contains a fix for this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-6393
- https://bitbucket.org/xi/libyaml
- https://bitbucket.org/xi/libyaml/commits/bce8b60f0b9af69fa9fab3093d0a41ba243de048
- https://bitbucket.org/xi/libyaml/commits/tag/0.1.5
- https://bugzilla.redhat.com/attachment.cgi?id=847926&action=diff
- https://bugzilla.redhat.com/show_bug.cgi?id=1033990
- https://puppet.com/security/cve/cve-2013-6393
- https://support.apple.com/kb/HT6536
- https://web.archive.org/web/20140302205713/http://www.securityfocus.com/bid/65258
- https://web.archive.org/web/20150523055002/http://www.mandriva.com/en/support/security/advisories/advisory/MDVSA-2015:060/?name=MDVSA-2015:060
- https://www.npmjs.com/advisories/21
- http://advisories.mageia.org/MGASA-2014-0040.html
- http://archives.neohapsis.com/archives/bugtraq/2014-04/0134.html
- http://archives.neohapsis.com/archives/bugtraq/2014-10/0103.html
- http://cve.mitre.org/cgi-bin/cvename.cgi?name=2013-6393
- http://lists.opensuse.org/opensuse-updates/2014-02/msg00064.html
- http://lists.opensuse.org/opensuse-updates/2014-02/msg00065.html
- http://lists.opensuse.org/opensuse-updates/2015-02/msg00078.html
- http://lists.opensuse.org/opensuse-updates/2016-04/msg00050.html
- http://rhn.redhat.com/errata/RHSA-2014-0353.html
