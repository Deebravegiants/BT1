# [H] Improper Access Control in Apache Derby

## Summary
Severity: High
Advisory: GHSA-xprw-xvvm-vqmv
CVE: CVE-2010-2232
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-xprw-xvvm-vqmv
Type: github-advisory

## Affected
- Maven: `org.apache.derby:derby` — affected >=10.1.2.1 <10.4.2.0

## Details
In Apache Derby 10.1.2.1, 10.2.2.0, 10.3.1.4, and 10.4.1.3, Export processing may allow an attacker to overwrite an existing file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-2232
- https://issues.apache.org/jira/browse/DERBY-2925
- http://db.apache.org/derby/releases/release-10.6.2.1.html#Note+for+DERBY-2925
