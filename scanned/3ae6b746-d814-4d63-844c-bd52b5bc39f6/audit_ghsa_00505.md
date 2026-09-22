# [H] Spring Data Commons, used in combination with XMLBeam, contains a property binder vulnerability caused by improper restriction of XML external entity references

## Summary
Severity: High
Advisory: GHSA-m929-7fr6-cvjg
CVE: CVE-2018-1259
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-m929-7fr6-cvjg
Type: github-advisory

## Affected
- Maven: `org.springframework.data:spring-data-commons` — affected >=1.13.0 <1.13.12
- Maven: `org.springframework.data:spring-data-commons` — affected >=2.0.0 <2.0.7

## Details
Spring Data Commons, versions 1.13 prior to 1.13.12 and 2.0 prior to 2.0.7, used in combination with XMLBeam 1.4.14 or earlier versions, contains a property binder vulnerability caused by improper restriction of XML external entity references as underlying library XMLBeam does not restrict external reference expansion. An unauthenticated remote malicious user can supply specially crafted request parameters against Spring Data's projection-based request payload binding to access arbitrary files on the system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1259
- https://access.redhat.com/errata/RHSA-2018:1809
- https://access.redhat.com/errata/RHSA-2018:3768
- https://github.com/advisories/GHSA-m929-7fr6-cvjg
- https://pivotal.io/security/cve-2018-1259
- https://www.oracle.com/security-alerts/cpujul2022.html
