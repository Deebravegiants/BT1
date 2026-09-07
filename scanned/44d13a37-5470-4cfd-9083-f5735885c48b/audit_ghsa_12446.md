# [C] XSS/CSRF Remote Code Execution in XWiki.ConfigurableClass

## Summary
Severity: Critical
Advisory: GHSA-cp3j-273x-3jxc
CVE: CVE-2023-50722
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-12-16
Source: https://github.com/advisories/GHSA-cp3j-273x-3jxc
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-administration-ui` — affected >=2.3 <14.10.15
- Maven: `org.xwiki.platform:xwiki-platform-administration-ui` — affected >=15.0-rc-1 <15.5.2
- Maven: `org.xwiki.platform:xwiki-platform-administration-ui` — affected >=15.6-rc-1 <15.7-rc-1

## Details
### Impact
 
There is a reflected XSS or also direct remote code execution vulnerability in the code for displaying configurable admin sections. The code that can be passed through a URL parameter is only executed when the user who is visiting the crafted URL has edit right on at least one configuration section. While any user of the wiki could easily create such a section, in this case it is much more convenient to exploit [GHSA-qj86-p74r-7wp5](https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-qj86-p74r-7wp5) which is why this attack scenario won't be further considered in the following. In contrast to GHSA-qj86-p74r-7wp5, this vulnerability doesn't require the attacker to have an account or any access on the wiki. It is sufficient to trick any admin user of the XWiki installation to visit the crafted URL. Alternatively, the URL can also be embedded as image source of an image in any content of the wiki like a comment that could be left by an anonymous user. This vulnerability allows full remote code execution with programming rights and thus impacts the confidentiality, integrity and availability of the whole XWiki installation.

### Patches

This has been fixed in XWiki 14.10.15, 15.5.2 and 15.7RC1

### Workarounds

The [patch](https://github.com/xwiki/xwiki-platform/commit/5e14c8d08fd0c5b619833d35090b470aa4cb52b0#diff-bf419a99140f3c12fd78ea30f855b63cfb74c1c976ff4436898266d9b37ad3ce) can be manually applied to the document `XWiki.ConfigurableClass`.

### References

* https://github.com/xwiki/xwiki-platform/commit/5e14c8d08fd0c5b619833d35090b470aa4cb52b0
* https://jira.xwiki.org/browse/XWIKI-21167

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-cp3j-273x-3jxc
- https://nvd.nist.gov/vuln/detail/CVE-2023-50722
- https://github.com/xwiki/xwiki-platform/commit/5e14c8d08fd0c5b619833d35090b470aa4cb52b0
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-21167
