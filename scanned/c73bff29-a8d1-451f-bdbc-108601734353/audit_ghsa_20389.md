# [H] Cross-site Scripting in Filter Stream Converter Application in XWiki Platform

## Summary
Severity: High
Advisory: GHSA-xjfw-5vv5-vjq2
CVE: CVE-2022-29258
CWE: CWE-116, CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2022-06-01
Source: https://github.com/advisories/GHSA-xjfw-5vv5-vjq2
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-filter-ui` — affected >=5.4.4 <12.10.11
- Maven: `org.xwiki.platform:xwiki-platform-filter-ui` — affected >=13.0.0 <13.4.7
- Maven: `org.xwiki.platform:xwiki-platform-filter-ui` — affected >=13.5.0 <13.10.3

## Details
### Impact
We found a possible XSS vector in the `Filter.FilterStreamDescriptorForm` wiki page related to pretty much all the form fields printed in the home page of the application.

### Patches
The issue is patched in versions 12.10.11, 14.0-rc-1, 13.4.7, 13.10.3.

### Workarounds
The easiest workaround is to edit the wiki page `Filter.FilterStreamDescriptorForm` (with wiki editor) and change the lines

```
          <input type="text" id="$descriptorId" name="$descriptorId" value="#if($request.get($descriptorId))$request.get($descriptorId)#else$descriptor.defaultValue#end"/>
        #else
          <input type="text" id="$descriptorId" name="$descriptorId"#if($request.get($descriptorId))value="$request.get($descriptorId)"#end/>
```

into

```
          <input type="text" id="$descriptorId" name="$descriptorId" value="#if($request.get($descriptorId))$escapetool.xml($request.get($descriptorId))#else$descriptor.defaultValue#end"/>
        #else
          <input type="text" id="$descriptorId" name="$descriptorId"#if($request.get($descriptorId))value="$escapetool.xml($request.get($descriptorId))"#end/>
```

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-xjfw-5vv5-vjq2
- https://nvd.nist.gov/vuln/detail/CVE-2022-29258
- https://github.com/xwiki/xwiki-platform/commit/21906acb5ee2304552f56f9bbdbf8e7d368f7f3a
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-19293
