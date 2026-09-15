# [M] Potential Captcha Validate Bypass in flask-session-captcha

## Summary
Severity: Medium
Advisory: GHSA-7r87-cj48-wj45
CVE: CVE-2022-24880
CWE: CWE-253, CWE-394, CWE-754
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-04-26
Source: https://github.com/advisories/GHSA-7r87-cj48-wj45
Type: github-advisory

## Affected
- PyPI: `flask-session-captcha` — affected >=0 <1.2.1

## Details
### Impact
flask-session-captcha is a package which allows users to extend Flask by adding an image based captcha stored in a server side session.

The `captcha.validate()` function would return `None` if passed no value (e.g. by submitting a request with an empty form).

If implementing users were checking the return value to be **False**, the captcha verification check could be bypassed.

Sample vulnerable code:
```python
if captcha.validate() == False:
    ... # abort
else:
   ... # do stuff
```

### Patches
A new version (1.2.1) is available that fixes the issue.

### Workarounds
Users can workaround the issue by not explicitly checking that the value is False. 

Checking the return value less explicitly should still work. 

```python
if not captcha.validate():
    ... # abort
else:
   ... # do stuff
```

```python
if captcha.validate():
    ... # do stuff
else:
   ... # abort
```

### References
https://github.com/Tethik/flask-session-captcha/pull/27

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [the github repo](https://github.com/Tethik/flask-session-captcha)

## References
- https://github.com/Tethik/flask-session-captcha/security/advisories/GHSA-7r87-cj48-wj45
- https://nvd.nist.gov/vuln/detail/CVE-2022-24880
- https://github.com/Tethik/flask-session-captcha/pull/27
- https://github.com/Tethik/flask-session-captcha/commit/2811ae23a38d33b620fb7a07de8837c6d65c13e4
- https://github.com/Tethik/flask-session-captcha
- https://github.com/Tethik/flask-session-captcha/releases/tag/v1.2.1
- https://github.com/pypa/advisory-database/tree/main/vulns/flask-session-captcha/PYSEC-2022-193.yaml
