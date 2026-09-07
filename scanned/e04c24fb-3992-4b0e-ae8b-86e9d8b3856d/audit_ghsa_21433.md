# [H] Cross Site Scripting vulnerability in wsgidav when directory browsing is enabled

## Summary
Severity: High
Advisory: GHSA-xx6g-jj35-pxjv
CVE: CVE-2022-41905
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2022-11-16
Source: https://github.com/advisories/GHSA-xx6g-jj35-pxjv
Type: github-advisory

## Affected
- PyPI: `wsgidav` — affected >=3.0.0a1 <4.1.0

## Details
### Impact
Implementations using this library with directory browsing enabled may be susceptible to [Cross Site Scripting (XSS)](https://owasp.org/www-community/attacks/xss/) attacks.

### Patches
Users can upgrade to v4.1.0

### Workarounds
Set `dir_browser.enable = False` in the configuration. For instance, when using a Python dictionary to configure the library:

```
config = {
    # your normal configuration
    "dir_browser": {
      "enable": False
    },
}
app = WsgiDAVApp(config)
```

### For more information

Note that an attacker cannot exploit this vulnerability, by simply  uploading a file or folder with a manipulated file name.
However if the WsgiDAV library is used in a scenario where untrusted data is displayed in the directory browser's user interface (e.g. 'realm' or user name, ...) XSS may happen.

If you have any questions or comments about this advisory:
* Open an issue in [mar10/wsgidav](https://github.com/mar10/wsgidav/)
* See the [security policy](https://github.com/mar10/wsgidav/security/policy)

## References
- https://github.com/mar10/wsgidav/security/advisories/GHSA-xx6g-jj35-pxjv
- https://nvd.nist.gov/vuln/detail/CVE-2022-41905
- https://github.com/mar10/wsgidav/commit/e9606ab0f42f4c1a6611bc3c52de299b0aba7726
- https://github.com/mar10/wsgidav
- https://github.com/pypa/advisory-database/tree/main/vulns/wsgidav/PYSEC-2022-43018.yaml
