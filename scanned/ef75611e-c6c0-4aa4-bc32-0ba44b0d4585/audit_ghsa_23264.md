# [M] Improper Input Validation in libpam4j

## Summary
Severity: Medium
Advisory: GHSA-x9rg-q5fx-fx66
CVE: CVE-2017-12197
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-x9rg-q5fx-fx66
Type: github-advisory

## Affected
- Maven: `org.kohsuke:libpam4j` — affected >=0 <1.10

## Details
It was found that libpam4j prior to 1.10 did not properly validate user accounts when authenticating. A user with a valid password for a disabled account would be able to bypass security restrictions and possibly access sensitive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12197
- https://github.com/kohsuke/libpam4j/issues/18
- https://github.com/kohsuke/libpam4j/commit/02ffdff218283629ba4a902e7fe2fd44646abc21
- https://access.redhat.com/errata/RHSA-2017:2904
- https://access.redhat.com/errata/RHSA-2017:2905
- https://access.redhat.com/errata/RHSA-2017:2906
- https://bugzilla.redhat.com/show_bug.cgi?id=1503103
- https://github.com/kohsuke/libpam4j
- https://lists.debian.org/debian-lts-announce/2017/11/msg00008.html
- https://www.debian.org/security/2017/dsa-4025
