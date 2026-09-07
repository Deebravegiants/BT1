# [C] XWiki allows SQL injection in query endpoint of REST API with Oracle

## Summary
Severity: Critical
Advisory: GHSA-prwh-7838-xf82
CVE: CVE-2024-56158
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-06-12
Source: https://github.com/advisories/GHSA-prwh-7838-xf82
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=1.0 <15.10.16
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=16.0.0-rc-1 <16.4.7
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=16.5.0-rc-1 <16.10.2

## Details
### Impact

It's possible to execute any SQL query in Oracle by using the function like [DBMS_XMLGEN or DBMS_XMLQUERY](https://docs.oracle.com/en/database/oracle/oracle-database/19/arpls/DBMS_XMLGEN.html).

The XWiki query validator does not sanitize functions that would be used in a simple `select` and Hibernate allows using any native function in an HQL query.

### Patches

This has been patched in 16.10.2, 16.4.7 and 15.10.16.

### Workarounds

There is no known workaround, other than upgrading XWiki.

### References

https://jira.xwiki.org/browse/XWIKI-22734

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-prwh-7838-xf82
- https://nvd.nist.gov/vuln/detail/CVE-2024-56158
- https://github.com/xwiki/xwiki-platform/commit/ce855aae38eefd8ee3fc86353d51ac03d6cb7f8d
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-22734
