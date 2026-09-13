# [H] XWiki allows unregistered users to access private pages information through REST endpoint

## Summary
Severity: High
Advisory: GHSA-22q5-9phm-744v
CVE: CVE-2025-29925
CWE: CWE-402
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-03-19
Source: https://github.com/advisories/GHSA-22q5-9phm-744v
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-rest-server` — affected >=1.9M1 <15.10.14
- Maven: `org.xwiki.platform:xwiki-platform-rest-server` — affected >=16.0.0-rc-1 <16.4.6
- Maven: `org.xwiki.platform:xwiki-platform-rest-server` — affected >=16.5.0-rc-1 <16.10.0-rc-1

## Details
### Impact

Protected pages are listed when requesting the REST endpoints `/rest/wikis/[wikiName]/pages` even if the user doesn't have view rights on them. 
It's particularly true if the entire wiki is protected with "Prevent unregistered user to view pages": the endpoint would still list the pages of the wiki (actually it only impacts the main wiki due to XWIKI-22639).

### Patches

The problem has been patched in XWiki 15.10.14, 16.4.6, 16.10.0RC1. In those versions the endpoint can still be requested but the result is filtered out based on pages rights.

### Workarounds

There's no workaround except upgrading or applying manually the changes of the commits (see references) in `xwiki-platform-rest-server` and recompiling / rebuilding it.

### References

 * Original JIRA ticket: https://jira.xwiki.org/browse/XWIKI-22630
 * Related JIRA ticket: https://jira.xwiki.org/browse/XWIKI-22639
 * Commits of the patch: https://github.com/xwiki/xwiki-platform/commit/bca72f5ce971a31dba2a016d8dd8badda4475206 and https://github.com/xwiki/xwiki-platform/commit/1fb12d2780f37b34a1b4dfdf8457d97ce5cbb2df

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-22q5-9phm-744v
- https://nvd.nist.gov/vuln/detail/CVE-2025-29925
- https://github.com/xwiki/xwiki-platform/commit/1fb12d2780f37b34a1b4dfdf8457d97ce5cbb2df
- https://github.com/xwiki/xwiki-platform/commit/bca72f5ce971a31dba2a016d8dd8badda4475206
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-22630
- https://jira.xwiki.org/browse/XWIKI-22639
