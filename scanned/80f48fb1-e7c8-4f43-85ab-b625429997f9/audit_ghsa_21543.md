# [C] Missing Authorization in Filter Stream Converter Application of XWiki-platform

## Summary
Severity: Critical
Advisory: GHSA-q6jp-gcww-8v2j
CVE: CVE-2022-41937
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-q6jp-gcww-8v2j
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-filter-ui` — affected >=0 <13.10.8
- Maven: `org.xwiki.platform:xwiki-platform-filter-ui` — affected >=14.0.0 <14.4.3
- Maven: `org.xwiki.platform:xwiki-platform-filter-ui` — affected >=14.5.0 <14.6-rc-1

## Details
### Impact

The application allow anyone with view access to modify any page of the wiki by importing a crafted XAR package.

### Patches

The problem has been patched in XWiki 14.6RC1, 14.6 and 13.10.8.

### Workarounds

The problem can be patched immediately by setting the right of the page Filter.WebHome and making sure only main wiki administrators can VIEW it the application is installed on main wiki or edit the page and apply the changed described on  https://github.com/xwiki/xwiki-platform/commit/fb49b4f289ee28e45cfada8e97e320cd3ed27113.

### References

* https://github.com/xwiki/xwiki-platform/commit/fb49b4f289ee28e45cfada8e97e320cd3ed27113
* https://jira.xwiki.org/browse/XWIKI-19758

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [JIRA](https://jira.xwiki.org)
* Email us at [security ML](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-q6jp-gcww-8v2j
- https://nvd.nist.gov/vuln/detail/CVE-2022-41937
- https://github.com/xwiki/xwiki-platform/commit/fb49b4f289ee28e45cfada8e97e320cd3ed27113
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-19758
