# [H] TabberNeue vulnerable to Stored XSS through wikitext

## Summary
Severity: High
Advisory: GHSA-jfj7-249r-7j2m
CVE: CVE-2025-53093
CWE: CWE-79, CWE-80
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2025-06-27
Source: https://github.com/advisories/GHSA-jfj7-249r-7j2m
Type: github-advisory

## Affected
- Packagist: `starcitizentools/tabber-neue` — affected >=3.0.0 <3.1.1

## Details
### Summary
Arbitrary HTML can be inserted into the DOM by inserting a payload into any allowed attribute of the `<tabber>` tag.

### Details

The `args` provided within the wikitext as attributes to the `<tabber>` tag are passed to the TabberComponentTabs class:
https://github.com/StarCitizenTools/mediawiki-extensions-TabberNeue/blob/3a23b703ce36cfc4128e7921841f68230be4059a/includes/Tabber.php#L76

In TabberComponentTabs, the attributes are validated before being supplied to the Tabs template.
https://github.com/StarCitizenTools/mediawiki-extensions-TabberNeue/blob/3a23b703ce36cfc4128e7921841f68230be4059a/includes/Components/TabberComponentTabs.php#L15-L31
However, the validation is insufficient.
What `Sanitizer::validateTagAttributes` does is call `validateAttributes`, which
```
	 * - Discards attributes not on the given list
	 * - Unsafe style attributes are discarded
	 * - Invalid id attributes are re-encoded
```
However, the attribute values are expected to be escaped when inserted into HTML.

The attribute values are then inserted into HTML without being escaped:
https://github.com/StarCitizenTools/mediawiki-extensions-TabberNeue/blob/3a23b703ce36cfc4128e7921841f68230be4059a/includes/templates/Tabs.mustache#L1

### PoC
#### XSS through attributes:
1. Go to Special:ExpandTemplates and insert the following wikitext:
```
<tabber class='test123" onmouseenter="alert(1)"'>
|-|First Tab Title=
First tab content goes here.
</tabber>
```
2. Press "OK"
3. Hover over the tabber

![image](https://github.com/user-attachments/assets/bb65a587-e277-4936-b9f9-400ad7c39040)


#### XSS through script tags:
1. Go to Special:ExpandTemplates and insert the following wikitext:
```
<tabber class='test123"&gt;&lt;script&gt;alert(2)&lt;/script&gt;'>
|-|First Tab Title=
First tab content goes here.
</tabber>
```
2. Press "OK"
![image](https://github.com/user-attachments/assets/a51ede5c-f9a0-49be-875e-37d30a083721)

### Impact
Arbitrary HTML can be inserted into the DOM by any user, allowing for JavaScript to be executed.

## References
- https://github.com/StarCitizenTools/mediawiki-extensions-TabberNeue/security/advisories/GHSA-jfj7-249r-7j2m
- https://nvd.nist.gov/vuln/detail/CVE-2025-53093
- https://github.com/StarCitizenTools/mediawiki-extensions-TabberNeue/commit/4cdf217ef96da74a1503d1dd0bb0ed898fc2a612
- https://github.com/StarCitizenTools/mediawiki-extensions-TabberNeue/commit/62ce0fcdf32bd3cfa77f92ff6b940459a14315fa
- https://github.com/StarCitizenTools/mediawiki-extensions-TabberNeue
- https://github.com/StarCitizenTools/mediawiki-extensions-TabberNeue/blob/3a23b703ce36cfc4128e7921841f68230be4059a/includes/Components/TabberComponentTabs.php#L15-L31
- https://github.com/StarCitizenTools/mediawiki-extensions-TabberNeue/blob/3a23b703ce36cfc4128e7921841f68230be4059a/includes/Tabber.php#L76
- https://github.com/StarCitizenTools/mediawiki-extensions-TabberNeue/blob/3a23b703ce36cfc4128e7921841f68230be4059a/includes/templates/Tabs.mustache#L1
