# [H] XWiki Platform vulnerable to SQL injection through XWiki#searchDocuments API

## Summary
Severity: High
Advisory: GHSA-p9qm-p942-q3w5
CVE: CVE-2025-54385
CWE: CWE-20, CWE-89
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-07-25
Source: https://github.com/advisories/GHSA-p9qm-p942-q3w5
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=1.0 <16.10.6
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=17.0.0-rc1 <17.3.0-rc-1

## Details
### Impact

It's possible to execute any SQL query in Oracle by using the function like [DBMS_XMLGEN or DBMS_XMLQUERY](https://docs.oracle.com/en/database/oracle/oracle-database/19/arpls/DBMS_XMLGEN.html).

The XWiki#searchDocuments APIs are not sanitizing the query at all and even if they force a specific select, Hibernate allows using any native function in an HQL query (for example in the WHERE).

### Patches

This has been patched in 16.10.6 and 17.3.0-rc-1.

### Workarounds

There is no known workaround, other than upgrading XWiki.

### References

https://jira.xwiki.org/browse/XWIKI-22728

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-p9qm-p942-q3w5
- https://nvd.nist.gov/vuln/detail/CVE-2025-54385
- https://github.com/xwiki/xwiki-platform/commit/7313dc9b533c70f14b7672379c8b3b63d1fd8f51
- https://github.com/xwiki/xwiki-platform/commit/7c4087d44ac550610b2fa413dd4f5375409265a5
- https://docs.oracle.com/en/database/oracle/oracle-database/19/arpls/DBMS_XMLGEN.html
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-22728
- https://www.xwiki.org/xwiki/bin/view/ReleaseNotes/Data/XWiki/16.10.6
