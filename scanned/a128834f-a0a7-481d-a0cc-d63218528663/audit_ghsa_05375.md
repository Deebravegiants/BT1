# [H] Apache Solr: Insufficient file-access checking in standalone core-creation requests

## Summary
Severity: High
Advisory: GHSA-vc2w-4v3p-2mqw
CVE: CVE-2026-22444
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-vc2w-4v3p-2mqw
Type: github-advisory

## Affected
- Maven: `org.apache.solr:solr-core` — affected >=8.6.0 <9.10.1

## Details
The "create core" API of Apache Solr 8.6 through 9.10.0 lacks sufficient input validation on some API parameters, which can cause Solr to check the existence of and attempt to read file-system paths that should be disallowed by Solr's  "allowPaths" security setting https://https://solr.apache.org/guide/solr/latest/configuration-guide/configuring-solr-xml.html#the-solr-element .  These read-only accesses can allow users to create cores using unexpected configsets if any are accessible via the filesystem.  On Windows systems configured to allow UNC paths this can additionally cause disclosure of NTLM "user" hashes. 

Solr deployments are subject to this vulnerability if they meet the following criteria:
  *  Solr is running in its "standalone" mode.
  *  Solr's "allowPath" setting is being used to restrict file access to certain directories.
  *  Solr's "create core" API is exposed and accessible to untrusted users.  This can happen if Solr's  RuleBasedAuthorizationPlugin https://solr.apache.org/guide/solr/latest/deployment-guide/rule-based-authorization-plugin.html  is disabled, or if it is enabled but the "core-admin-edit" predefined permission (or an equivalent custom permission) is given to low-trust (i.e. non-admin) user roles.

Users can mitigate this by enabling Solr's RuleBasedAuthorizationPlugin (if disabled) and configuring a permission-list that prevents untrusted users from creating new Solr cores.  Users should also upgrade to Apache Solr 9.10.1 or greater, which contain fixes for this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-22444
- https://github.com/apache/solr
- https://issues.apache.org/jira/browse/SOLR-18058
- https://lists.apache.org/thread/qkrb9dd4xrlqmmq73lrhkbfkttto2d1m
- http://www.openwall.com/lists/oss-security/2026/01/20/5
