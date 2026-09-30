# [M] Loop with Unreachable Exit Condition in Apache POI

## Summary
Severity: Medium
Advisory: GHSA-x9mm-6gpf-f749
CVE: CVE-2014-9527
CWE: CWE-835
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-x9mm-6gpf-f749
Type: github-advisory

## Affected
- Maven: `org.apache.poi:poi` — affected >=0 <3.11

## Details
HSLFSlideShow in Apache POI before 3.11 allows remote attackers to cause a denial of service (infinite loop and deadlock) via a crafted PPT file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-9527
- https://access.redhat.com/errata/RHSA-2016:1135
- https://issues.apache.org/bugzilla/show_bug.cgi?id=57272
- http://lists.fedoraproject.org/pipermail/package-announce/2015-February/150228.html
- http://poi.apache.org/changes.html
- http://secunia.com/advisories/61953
- http://www-01.ibm.com/support/docview.wss?uid=swg21996759
