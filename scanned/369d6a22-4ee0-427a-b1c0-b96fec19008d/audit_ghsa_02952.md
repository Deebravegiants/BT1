# [M] Apache Ozone exposes OM, SCM and Datanode metadata

## Summary
Severity: Medium
Advisory: GHSA-gc37-9g7f-96fx
CVE: CVE-2021-41532
CWE: CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-11-23
Source: https://github.com/advisories/GHSA-gc37-9g7f-96fx
Type: github-advisory

## Affected
- Maven: `org.apache.ozone:ozone-main` — affected >=0 <1.2.0

## Details
In Apache Ozone before 1.2.0, Recon HTTP endpoints provide access to OM, SCM and Datanode metadata. Due to a bug, any unauthenticated user can access the data from these endpoints.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41532
- https://mail-archives.apache.org/mod_mbox/ozone-dev/202111.mbox/%3Ce0bc6598-9669-b897-fc28-de8a896e36aa%40apache.org%3E
- http://www.openwall.com/lists/oss-security/2021/11/19/8
