# [C] Django Template Engine Vulnerable to XSS

## Summary
Severity: Critical
Advisory: GHSA-4mq2-gc4j-cmw6
CVE: CVE-2024-22199
CWE: CWE-116, CWE-20, CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2024-01-11
Source: https://github.com/advisories/GHSA-4mq2-gc4j-cmw6
Type: github-advisory

## Affected
- Go: `github.com/gofiber/template/django/v3` — affected >=0 <3.1.9

## Details
### Impact

**Vulnerability Type:** Cross-Site Scripting (XSS)  
**Affected Users:** All users of the Django template engine for Fiber prior to the patch. This vulnerability specifically impacts web applications that render user-supplied data through this template engine, potentially leading to the execution of malicious scripts in users' browsers when visiting affected web pages.

### Patches

The vulnerability has been addressed. The template engine now defaults to having autoescape set to `true`, effectively mitigating the risk of XSS attacks. Users are advised to upgrade to the latest version of the Django template engine for Fiber, where this security update is implemented. Ensure that the version of the template engine being used is the latest, post-patch version.

### Workarounds

For users unable to upgrade immediately to the patched version, a workaround involves manually implementing autoescaping within individual Django templates. This method includes adding specific tags in the template to control autoescape behavior:
```django
{% autoescape on %}
{{ "<script>alert('xss');</script>" }}
{% endautoescape %}
```

### References

- Official documentation of the Django template engine for Fiber: https://docs.gofiber.io/template/django/
- Django built-in template tags: https://docs.djangoproject.com/en/5.0/ref/templates/builtins/

## References
- https://github.com/gofiber/template/security/advisories/GHSA-4mq2-gc4j-cmw6
- https://nvd.nist.gov/vuln/detail/CVE-2024-22199
- https://github.com/gofiber/template/commit/28cff3ac4d4c117ab25b5396954676d624b6cb46
- https://github.com/gofiber/template
