# [M] Cross-Site Request Forgery (CSRF) Protection Bypass Vulnerability in CodeIgniter4

## Summary
Severity: Medium
Advisory: GHSA-4v37-24gm-h554
CVE: CVE-2022-24712
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2022-03-01
Source: https://github.com/advisories/GHSA-4v37-24gm-h554
Type: github-advisory

## Affected
- Packagist: `codeigniter4/framework` — affected >=0 <4.1.9

## Details
### Impact
This vulnerability might allow remote attackers to bypass the CodeIgniter4 CSRF protection mechanism. 

### Patches
Upgrade to v4.1.9 or later.

### Workarounds
These are workarounds for this vulnerability, but **you will still need to code as these after upgrading to v4.1.9**.
Otherwise, the CSRF protection may be bypassed.

#### When Auto-Routing is Enabled
1. Check the request method in the controller method before processing.

E.g.:
```php
        if (strtolower($this->request->getMethod()) !== 'post') {
            return $this->response->setStatusCode(405)->setBody('Method Not Allowed');
        }
```

#### When Auto-Routing is Disabled
Do one of the following:
1. Do not use `$routes->add()`, and [use HTTP verbs in routes](https://codeigniter4.github.io/userguide/incoming/routing.html#using-http-verbs-in-routes).
2. Check the request method in the controller method before processing.

E.g.:
```php
        if (strtolower($this->request->getMethod()) !== 'post') {
            return $this->response->setStatusCode(405)->setBody('Method Not Allowed');
        }
```

### References
- [CodeIgniter4 CSRF protection](https://codeigniter4.github.io/userguide/libraries/security.html#cross-site-request-forgery-csrf)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [codeigniter4/CodeIgniter4](https://github.com/codeigniter4/CodeIgniter4/issues)
* Email us at [SECURITY.md](https://github.com/codeigniter4/CodeIgniter4/blob/develop/SECURITY.md)

## References
- https://github.com/codeigniter4/CodeIgniter4/security/advisories/GHSA-4v37-24gm-h554
- https://nvd.nist.gov/vuln/detail/CVE-2022-24712
- https://github.com/codeigniter4/CodeIgniter4/blob/7dc2ece32401ebde67122f7d2460efcaee7c352e/user_guide_src/source/changelogs/v4.1.9.rst
