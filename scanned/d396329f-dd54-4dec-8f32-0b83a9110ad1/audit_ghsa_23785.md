# [M] Improper Control of Generation of Code in HawtJNI

## Summary
Severity: Medium
Advisory: GHSA-49j7-qghp-5wj8
CVE: CVE-2013-2035
CWE: CWE-94
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-49j7-qghp-5wj8
Type: github-advisory

## Affected
- Maven: `org.fusesource.hawtjni:hawtjni-runtime` — affected >=0 <1.8

## Details
Race condition in hawtjni-runtime/src/main/java/org/fusesource/hawtjni/runtime/Library.java in HawtJNI before 1.8, when a custom library path is not specified, allows local users to execute arbitrary Java code by overwriting a temporary JAR file with a predictable name in /tmp.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2035
- https://github.com/jline/jline2/issues/85
- https://github.com/jruby/jruby/issues/732
- https://github.com/fusesource/hawtjni/commit/92c266170ce98edc200c656bd034a237098b8aa5
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2013-2035
- http://rhn.redhat.com/errata/RHSA-2013-1029.html
- http://rhn.redhat.com/errata/RHSA-2013-1784.html
- http://rhn.redhat.com/errata/RHSA-2013-1785.html
- http://rhn.redhat.com/errata/RHSA-2013-1786.html
- http://rhn.redhat.com/errata/RHSA-2014-0029.html
- http://rhn.redhat.com/errata/RHSA-2014-0245.html
- http://rhn.redhat.com/errata/RHSA-2014-0254.html
- http://rhn.redhat.com/errata/RHSA-2014-0400.html
- http://rhn.redhat.com/errata/RHSA-2015-0034.html
- http://www.osvdb.org/93411
