# [M] Opencast's Paella Player 7 is vulnerable to Cross-Site Scripting

## Summary
Severity: Medium
Advisory: GHSA-m2vg-rmq6-p62r
CVE: CVE-2025-61788
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-10-08
Source: https://github.com/advisories/GHSA-m2vg-rmq6-p62r
Type: github-advisory

## Affected
- Maven: `org.opencastproject:opencast-common` — affected >=0

## Details
Prior to Opencast 17.8 and 18.2 the paella would include and render some user inputs (metadata like title, description, etc.) unfiltered and unmodified.

### Impact

The vulnerability allows attackers to inject and malicious HTML and JavaScript in the player, which would then be executed in the browsers of users watching the prepared media. This can then be used to modify the site or to execute actions in the name of logged-in users.

To inject malicious metadata, an attacker needs write access to the system. For example, the ability to upload media and modify metadata. This cannot be exploited by unauthenticated users.

### Patches

This issue is fixed in Opencast 17.8 and 18.2, however they are not published to the Maven registry.

### Resources

- [Patch fixing the issue](https://github.com/opencast/opencast/commit/2809520fa88d108d8104c760f00c10bad42c14f9)

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [our issue tracker](https://github.com/opencast/opencast/issues)
* Email us at [security@opencast.org](mailto:security@opencast.org)

## References
- https://github.com/opencast/opencast/security/advisories/GHSA-m2vg-rmq6-p62r
- https://nvd.nist.gov/vuln/detail/CVE-2025-61788
- https://github.com/opencast/opencast/commit/2809520fa88d108d8104c760f00c10bad42c14f9
- https://github.com/opencast/opencast
