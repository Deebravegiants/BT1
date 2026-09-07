# [M] WebOb: Location header normalization during redirect leads to open redirect - again

## Summary
Severity: Medium
Advisory: GHSA-fh3h-vg37-cc95
CVE: CVE-2026-44889
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-fh3h-vg37-cc95
Type: github-advisory

## Affected
- PyPI: `webob` — affected >=0 <1.8.10

## Details
### Impact

When WebOb normalizes the HTTP Location header to include the request hostname, it does so by parsing the URL that the user is to be redirected to with Python's `urllib.parse`, and joining it to the base URL. `urlsplit` (called internally by `urljoin`) however treats a `//` at the start of a string as a URI without a scheme, and then treats the next part as the hostname. `urljoin` will then use that hostname from the second part as the hostname replacing the original one from the request.

In a previous advisory https://github.com/Pylons/webob/security/advisories/GHSA-mg3v-6m49-jhp3 an attempt to fix this was made by forcing the replacement of `//` with `/%2f`, however this did not take into account that since Python 3.10 `urlsplit` internally strips ASCII tab, carriage return, and newline characters from the string, so `/\t/attacker.com` gets turned into `//attacker.com` and the attacker is able to bypass the changes introduced in that previous advisory, thereby bringing back the problem that was attempted to be fixed.

```
>>> parse.urlparse("//attacker.com/some/path")
ParseResult(scheme='', netloc='attacker.com', path='/some/path', params='', query='', fragment='')
```

WebOb uses `urljoin` to take the request URI and join the redirect location to it, so assuming the request URI is `https://example.org/` and the URL to redirect to is `/\t/attacker.com/some/path/`:

```
>>> parse.urljoin("https://example.org/", "/\t/attacker.com/some/path/")
'https://attacker.com/some/path/'
```

Which redirects from `example.org` where we want the user to stay to `attacker.com`.

### Patches

This issue has been fixed in WebOb 1.8.10.

### Workarounds

Any use of the `Response` class that includes a `location` can be rewritten to make sure to always pass a full URI that includes the hostname to redirect the user to, or to validate that the redirect target starts with a scheme (e.g. `http://` or `https://`) before assigning to `Response.location`.

### References

- https://github.com/Pylons/webob/security/advisories/GHSA-mg3v-6m49-jhp3
- CVE-2024-42353

### Thanks

- Caleb Brown of Google

## References
- https://github.com/Pylons/webob/security/advisories/GHSA-fh3h-vg37-cc95
- https://github.com/Pylons/webob/security/advisories/GHSA-mg3v-6m49-jhp3
- https://nvd.nist.gov/vuln/detail/CVE-2026-44889
- https://github.com/Pylons/webob/commit/1f681a4f17fc10777ef861e8b43ecb26053bc539
- https://github.com/Pylons/webob/commit/2b9fbedafb31180c910cf8526e9ea72b4603d0bc
- https://github.com/Pylons/webob
- https://github.com/Pylons/webob/releases/tag/1.8.10
- https://github.com/pypa/advisory-database/tree/main/vulns/webob/PYSEC-2026-251.yaml
