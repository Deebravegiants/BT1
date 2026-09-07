# [M] Unregistered users can see "public" messages from a closed wiki via notifications from a different wiki

## Summary
Severity: Medium
Advisory: GHSA-42fh-pvvh-999x
CVE: CVE-2025-32783
CWE: CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2025-04-16
Source: https://github.com/advisories/GHSA-42fh-pvvh-999x
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-messagestream` — affected >=5.0

## Details
### Impact

This vulnerability impacts users of a subwiki of XWiki where Message Stream is enabled and use, if they configured their wiki to be closed by selecting "Prevent unregistered users to view pages" in the Administrations Rights. 

The vulnerability is that any message sent in a subwiki to "everyone" is actually sent to the farm: any visitor of the main wiki will be able to see that message through the Dashboard, even if the subwiki is configured to be private.

### Patches

This problem has not been patched and is not going to be patched in the future: Message Stream has been deprecated in XWiki 16.8.0RC1 and is not maintained anymore. 

### Workarounds

Message Stream is disabled by default, it's advised to keep it disabled from Administration > Social > Message Stream.

### References

  * https://jira.xwiki.org/browse/XWIKI-17154

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-42fh-pvvh-999x
- https://nvd.nist.gov/vuln/detail/CVE-2025-32783
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-17154
