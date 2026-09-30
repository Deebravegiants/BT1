# [M] Apache Derby exposes user and password attributes

## Summary
Severity: Medium
Advisory: GHSA-rp7r-79rm-2758
CVE: CVE-2005-4849
CWE: CWE-200
Ecosystem: Maven
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-rp7r-79rm-2758
Type: github-advisory

## Affected
- Maven: `org.apache.derby:derby` — affected >=0 <10.1.2.1

## Details
Apache Derby before 10.1.2.1 exposes the (1) user and (2) password attributes in cleartext via (a) the RDBNAM parameter of the ACCSEC command and (b) the output of the DatabaseMetaData.getURL function, which allows context-dependent attackers to obtain sensitive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2005-4849
- https://github.com/apache/derby/commit/09a7325f75a4f96a7735e46c9723930f88ea2613
- https://github.com/apache/derby/commit/82d721fd53e30dbb86d6d742c085030985091968
- https://github.com/apache/derby/commit/fd24a7590ff5426bac68303fbeca07dbc5067412
- https://github.com/apache/derby
- http://db.apache.org/derby/releases/release-10.1.2.1.html
- http://issues.apache.org/jira/browse/DERBY-530
- http://issues.apache.org/jira/browse/DERBY-559
- http://svn.apache.org/viewvc?view=revision&revision=289672
