# [M] OAuthLib vulnerable to DoS when attacker provides malicious IPV6 URI

## Summary
Severity: Medium
Advisory: GHSA-3pgj-pg6c-r5p7
CVE: CVE-2022-36087
CWE: CWE-20, CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-3pgj-pg6c-r5p7
Type: github-advisory

## Affected
- PyPI: `oauthlib` — affected >=3.1.1 <3.2.2

## Details
### Impact
- Attacker providing malicious redirect uri can cause DoS to oauthlib's web application.
- Attacker can also leverage usage of `uri_validate` functions depending where it is used.

_What kind of vulnerability is it? Who is impacted?_

Oauthlib applications using OAuth2.0 provider support or use directly `uri_validate` function.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

Issue fixed in 3.2.2 release.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

The `redirect_uri` can be verified in web toolkit (i.e `bottle-oauthlib`, `django-oauth-toolkit`, ...) before oauthlib is called. A sample check if `:` is present to reject the request can prevent the DoS, assuming no port or IPv6 is fundamentally required.

### References
Attack Vector:
- Attacker providing malicious redirect uri:
https://github.com/oauthlib/oauthlib/blob/d4bafd9f1d0eba3766e933b1ac598cbbf37b8914/oauthlib/oauth2/rfc6749/grant_types/base.py#L232
- Vulnerable `uri_validate` functions:
https://github.com/oauthlib/oauthlib/blob/2b8a44855a51ad5a5b0c348a08c2564a2e197ea2/oauthlib/uri_validate.py

### PoC
```python
is_absolute_uri("http://[:::::::::::::::::::::::::::::::::::::::]/path")
```

### Acknowledgement
Special thanks to Sebastian Chnelik - PyUp.io

## References
- https://github.com/oauthlib/oauthlib/security/advisories/GHSA-3pgj-pg6c-r5p7
- https://nvd.nist.gov/vuln/detail/CVE-2022-36087
- https://github.com/oauthlib/oauthlib/commit/2e40b412c844ecc4673c3fa3f72181f228bdbacd
- https://github.com/oauthlib/oauthlib
- https://github.com/oauthlib/oauthlib/blob/2b8a44855a51ad5a5b0c348a08c2564a2e197ea2/oauthlib/uri_validate.py
- https://github.com/oauthlib/oauthlib/blob/d4bafd9f1d0eba3766e933b1ac598cbbf37b8914/oauthlib/oauth2/rfc6749/grant_types/base.py#L232
- https://github.com/oauthlib/oauthlib/releases/tag/v3.2.1
- https://github.com/pypa/advisory-database/tree/main/vulns/oauthlib/PYSEC-2022-269.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LXOPIA6M57CFQPUT6HHSNXCTV6QA3UDI
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NBCQJR3ZF7FVNTJYRVPVSQEQRAYZIUHU
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QRYLYHE5HWF6R2CRLJFUK4PILR47WXOE
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/X2CQZM5CKOUM4GW2GTAPQEQFPITQ6F7S
