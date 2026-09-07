# [M] Unsynchronized Access to Shared Data in a Multithreaded Context in RESTEasy

## Summary
Severity: Medium
Advisory: GHSA-9699-gm7f-cmjv
CVE: CVE-2020-25724
CWE: CWE-567
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-06-08
Source: https://github.com/advisories/GHSA-9699-gm7f-cmjv
Type: github-advisory

## Affected
- Maven: `org.jboss.resteasy:resteasy-bom` — affected >=0 <2.0-beta-2

## Details
A flaw was found in RESTEasy, where an incorrect response to an HTTP request is provided. This flaw allows an attacker to gain access to privileged information. The highest threat from this vulnerability is to confidentiality and integrity. Versions before resteasy 2.0.0.Alpha3 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25724
- https://access.redhat.com/security/cve/cve-2020-25724
- https://bugzilla.redhat.com/show_bug.cgi?id=1899354
- https://security.netapp.com/advisory/ntap-20210702-0003
