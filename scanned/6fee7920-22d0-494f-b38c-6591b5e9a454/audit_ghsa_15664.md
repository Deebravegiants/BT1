# [C] XWiki Platform vulnerable to Cross-Site Scripting (XSS) through conflict resolution

## Summary
Severity: Critical
Advisory: GHSA-692v-783f-mg8x
CVE: CVE-2024-41947
CWE: CWE-79, CWE-80
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-31
Source: https://github.com/advisories/GHSA-692v-783f-mg8x
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=11.8-rc-1 <15.10.8
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=16.0.0-rc-1 <16.3.0-rc-1

## Details
### Impact

By creating a conflict when another user with more rights is currently editing a page, it is possible to execute JavaScript snippets on the side of the other user, which compromises the confidentiality, integrity and availability of the whole XWiki installation.

To reproduce on a XWiki instance, a user with admin rights needs to edit a document without saving right away.
Then, as another user without any other right than edit on the specific document, change the whole content to `<script>alert('XSS')</script>`.
When the admin user then saves the document, a conflict popup appears. If they select "Fix each conflict individually" and see an alert displaying "XSS", then the instance is vulnerable.

### Patches

This has been patched in XWiki 15.10.8 and 16.3.0RC1.

### Workarounds

We're not aware of any workaround except upgrading.

### References

* https://jira.xwiki.org/browse/XWIKI-21626
* https://github.com/xwiki/xwiki-platform/commit/821d43ec45e67d45a6735a0717b9b77fffc1cd9f

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-692v-783f-mg8x
- https://nvd.nist.gov/vuln/detail/CVE-2024-41947
- https://github.com/xwiki/xwiki-platform/commit/821d43ec45e67d45a6735a0717b9b77fffc1cd9f
- https://github.com/xwiki/xwiki-platform/commit/e00e159d3737397eebd1f6ff925c1f5cb7cdec34
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-21626
