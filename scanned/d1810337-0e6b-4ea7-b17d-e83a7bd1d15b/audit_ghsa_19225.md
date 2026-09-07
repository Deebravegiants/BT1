# [M] Sulu vulnerable to XXE in SVG File upload Inspector

## Summary
Severity: Medium
Advisory: GHSA-f6rx-hf55-4255
CVE: CVE-2025-47778
CWE: CWE-611
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-05-15
Source: https://github.com/advisories/GHSA-f6rx-hf55-4255
Type: github-advisory

## Affected
- Packagist: `sulu/sulu` — affected >=2.5.21 <2.5.25
- Packagist: `sulu/sulu` — affected >=2.6.5 <2.6.9
- Packagist: `sulu/sulu` — affected >=3.0.0-alpha1 <3.0.0-alpha3

## Details
### Impact

A admin user can upload SVG which may load external data via XML DOM library, specially this can be used for eventually reference none secure XML External Entity References.

### Patches

The problem has not been patched yet. Users should upgrade to patched versions once they become available. Currently affected versions are:

 - 2.6.9
 - 2.5.25
 - 3.0.0-alpha3

### Workarounds

Patch the effect file `src/Sulu/Bundle/MediaBundle/FileInspector/SvgFileInspector.php` in sulu with:

```diff
-$dom->loadXML($svg, \LIBXML_NOENT | \LIBXML_DTDLOAD);
+$dom->loadXML($data, LIBXML_NONET);
```

### References

 - GitHub repository: https://github.com/sulu/sulu
 - Vulnerable code: https://github.com/sulu/sulu/blob/2.6/src/Sulu/Bundle/MediaBundle/FileInspector/SvgFileInspector.php

## References
- https://github.com/sulu/sulu/security/advisories/GHSA-f6rx-hf55-4255
- https://nvd.nist.gov/vuln/detail/CVE-2025-47778
- https://github.com/sulu/sulu/commit/02f52fca04eb9495b9b4a0c5cc64cf23bc27f544
- https://github.com/sulu/sulu
- https://github.com/sulu/sulu/blob/2.6/src/Sulu/Bundle/MediaBundle/FileInspector/SvgFileInspector.php
