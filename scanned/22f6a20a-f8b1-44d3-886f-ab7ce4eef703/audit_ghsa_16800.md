# [M] changedetection.io Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-pwgc-w4x9-gw67
CVE: CVE-2024-34061
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-05-03
Source: https://github.com/advisories/GHSA-pwgc-w4x9-gw67
Type: github-advisory

## Affected
- PyPI: `changedetection.io` — affected >=0 <0.45.22

## Details
### Summary

Input in parameter notification_urls is not processed resulting in javascript execution in the application

### Details
changedetection.io version: v0.45.21

https://github.com/dgtlmoon/changedetection.io/blob/0.45.21/changedetectionio/forms.py#L226

```
        for server_url in field.data:
            if not apobj.add(server_url):
                message = field.gettext('\'%s\' is not a valid AppRise URL.' % (server_url))
                raise ValidationError(message)
```

### PoC

Setting > ADD Notification URL List

![image](https://github.com/dgtlmoon/changedetection.io/assets/65381453/626eb43b-a414-4b05-92d8-c7345c2a2e75)


```
"><img src=x onerror=alert(document.domain)>
```
![image](https://github.com/dgtlmoon/changedetection.io/assets/65381453/476bd396-2aa2-4642-9c54-fd2c2ef9de79)

Requests

![image](https://github.com/dgtlmoon/changedetection.io/assets/65381453/1f258ef1-149a-4a03-88ab-a2244a69652e)


### Impact
A reflected XSS vulnerability happens when the user input from a URL or POST data is reflected on the page without being stored, thus allowing the attacker to inject malicious content

## References
- https://github.com/dgtlmoon/changedetection.io/security/advisories/GHSA-pwgc-w4x9-gw67
- https://nvd.nist.gov/vuln/detail/CVE-2024-34061
- https://github.com/dgtlmoon/changedetection.io/commit/c0f000b1d1ce03733460805dbbedde445fe2c762
- https://github.com/dgtlmoon/changedetection.io
- https://github.com/dgtlmoon/changedetection.io/blob/0.45.21/changedetectionio/forms.py#L226
