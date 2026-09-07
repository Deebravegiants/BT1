# [H] LibreNMS uses Improper Sanitization on Service template name leads to Stored XSS

## Summary
Severity: High
Advisory: GHSA-72m9-7c8x-pmmw
CVE: CVE-2024-32479
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-22
Source: https://github.com/advisories/GHSA-72m9-7c8x-pmmw
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0 <24.4.0

## Details
### Summary
There is improper sanitization on Service template name which is reflecting in delete button onclick event. This value can be modified and crafted as any other javascript code.

 
### Vulnerable Code
https://github.com/librenms/librenms/blob/a61c11db7e8ef6a437ab55741658be2be7d14d34/app/Http/Controllers/ServiceTemplateController.php#L67C23-L67C23

Above is vulnerable code line which needs to be properly sanitized 

### PoC
1. Go to /services/templates
2. Enter name as `testing', '14', 'http://172.105.62.194:8000/services/templates/14');alert(1);//`
3. Submit it and try to delete it, you will see popup

If you inspect element on delete button, you will notice this:-
<img width="748" alt="Screenshot 2023-11-23 at 9 30 24 PM" src="https://user-images.githubusercontent.com/31764504/285260018-7672a93d-e29b-4444-8057-e6ffcb8dabfc.png">


### Impact
Cross site scripting can lead to cookie stealing or an attacker can execute any other feature using this feature.

## References
- https://github.com/librenms/librenms/security/advisories/GHSA-72m9-7c8x-pmmw
- https://nvd.nist.gov/vuln/detail/CVE-2024-32479
- https://github.com/librenms/librenms/commit/19344f0584d4d6d4526fdf331adc60530e3f685b
- https://github.com/librenms/librenms
- https://github.com/librenms/librenms/blob/a61c11db7e8ef6a437ab55741658be2be7d14d34/app/Http/Controllers/ServiceTemplateController.php#L67C23-L67C23
