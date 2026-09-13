# [H] Incorrect Authorization in Apache Ozone

## Summary
Severity: High
Advisory: GHSA-ff84-84q5-fq4f
CVE: CVE-2021-39232
CWE: CWE-862, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-23
Source: https://github.com/advisories/GHSA-ff84-84q5-fq4f
Type: github-advisory

## Affected
- Maven: `org.apache.ozone:ozone-main` — affected >=0 <1.2.0

## Details
In Apache Ozone versions prior to 1.2.0, certain admin related SCM commands can be executed by any authenticated users, not just by admins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-39232
- https://github.com/apache/ozone
- https://mail-archives.apache.org/mod_mbox/ozone-dev/202111.mbox/%3C3c30a7f2-13a4-345e-6c8a-c23a2b937041%40apache.org%3E
- http://www.openwall.com/lists/oss-security/2021/11/19/3
