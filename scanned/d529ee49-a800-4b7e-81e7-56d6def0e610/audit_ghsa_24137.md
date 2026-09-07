# [M] Improper Input Validation in Apache Karaf

## Summary
Severity: Medium
Advisory: GHSA-m6g3-xq5q-4hg9
CVE: CVE-2014-0219
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-m6g3-xq5q-4hg9
Type: github-advisory

## Affected
- Maven: `org.apache.karaf:apache-karaf` — affected >=0 <4.0.10

## Details
Apache Karaf before 4.0.10 enables a shutdown port on the loopback interface, which allows local users to cause a denial of service (shutdown) by sending a shutdown command to all listening high ports.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0219
- https://bugzilla.redhat.com/show_bug.cgi?id=1095974
- http://karaf.apache.org/security/cve-2014-0219.txt
