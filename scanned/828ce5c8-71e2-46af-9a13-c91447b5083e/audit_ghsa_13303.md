# [C] org.xwiki.platform:xwiki-platform-skin-ui Eval Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-h4vp-69r8-gvjg
CVE: CVE-2023-37462
CWE: CWE-74, CWE-95
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-14
Source: https://github.com/advisories/GHSA-h4vp-69r8-gvjg
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-skin-ui` — affected >=7.0-rc-1 <14.4.8
- Maven: `org.xwiki.platform:xwiki-platform-skin-ui` — affected >=14.5 <14.10.4

## Details
### Impact

Improper escaping in the document `SkinsCode.XWikiSkinsSheet` leads to a possible privilege escalation from view right on that document to programming rights, or in other words, it is possible to execute arbitrary script macros including Groovy and Python macros that allow remote code execution including unrestricted read and write access to all wiki contents.

The attack works by opening a non-existing page with a name crafted to contain a dangerous payload.

It is possible to check if an existing installation is vulnerable by opening `<xwiki-host>/xwiki/bin/view/%22%5D%5D%20%7B%7Basync%20async%3D%22true%22%20cached%3D%22false%22%20context%3D%22doc.reference%22%7D%7D%7B%7Bgroovy%7D%7Dprintln(%22Hello%20%22%20%2B%20%22from%20groovy!%22)%7B%7B%2Fgroovy%7D%7D%7B%7B%2Fasync%7D%7D?sheet=SkinsCode.XWikiSkinsSheet&xpage=view` where <xwiki-host is the URL of the XWiki installation. The expected result are two list items with "Edit this skin" and "Test this skin" without any further text. If the installation is vulnerable, the second list item is "Test this skin Hello from groovy!.WebHome"]]". This shows that the Groovy macro has been executed.

### Patches

This has been patched in XWiki 14.4.8, 14.10.4 and 15.0-rc-1.

### Workarounds

The [fix](https://github.com/xwiki/xwiki-platform/commit/d9c88ddc4c0c78fa534bd33237e95dea66003d29) can also be applied manually to the impacted document `SkinsCode.XWikiSkinsSheet`.

### References

* https://jira.xwiki.org/browse/XWIKI-20457
* https://github.com/xwiki/xwiki-platform/commit/d9c88ddc4c0c78fa534bd33237e95dea66003d29

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-h4vp-69r8-gvjg
- https://nvd.nist.gov/vuln/detail/CVE-2023-37462
- https://github.com/xwiki/xwiki-platform/commit/d9c88ddc4c0c78fa534bd33237e95dea66003d29
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20457
