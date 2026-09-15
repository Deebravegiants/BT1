# [H] Unsafe handling of user-specified cookies in treq

## Summary
Severity: High
Advisory: GHSA-fhpf-pp6p-55qc
CVE: CVE-2022-23607
CWE: CWE-200, CWE-425, CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-01
Source: https://github.com/advisories/GHSA-fhpf-pp6p-55qc
Type: github-advisory

## Affected
- PyPI: `treq` — affected >=0 <22.1.0

## Details
### Impact

Treq's request methods (`treq.get`, `treq.post`, `HTTPClient.request`, `HTTPClient.get`, etc.) accept cookies as a dictionary, for example:

```py
treq.get('https://example.com/', cookies={'session': '1234'})
```

Such cookies are not bound to a single domain, and are therefore sent to *every* domain ("supercookies"). This can potentially cause sensitive information to leak upon an HTTP redirect to a different domain., e.g. should `https://example.com` redirect to `http://cloudstorageprovider.com` the latter will receive the cookie `session`.

### Patches

Treq 2021.1.0 and later bind cookies given to request methods (`treq.request`, `treq.get`, `HTTPClient.request`, `HTTPClient.get`, etc.) to the origin of the *url* parameter.

### Workarounds

Instead of passing a dictionary as the *cookies* argument, pass a `http.cookiejar.CookieJar` instance with properly domain- and scheme-scoped cookies in it:

```py
from http.cookiejar import CookieJar
from requests.cookies import create_cookie

jar = CookieJar()
jar.add_cookie(
    create_cookie(
        name='session',
        value='1234',
        domain='example.com',
        secure=True,
    ),
)
client = HTTPClient(cookies=jar)
client.get('https://example.com/')
```

### References

* Originally reported at [huntr.dev](https://huntr.dev/bounties/3c9204fc-a3d1-4441-8599-924c5f57e7ae/?token=06d930e37046c914bcb037e85cc227dc7b510b475989fc69837566562ba899277d46b0fb4b1e21cdcb6ddc1b7d9b1ded632cf3a3551ecb89afca16a63b34641284b50479d5195bba2ac09b116f3dd4fad27f54404c2de922c05c8c8b744aec27bb4d4d198cb8b3abf479af0c2d5fbaa10412da7922594ac3eb39)
* A related issue in the handling of HTTP basic authentication was addressed in Twisted 22.1 ([GHSA-92x2-jw7w-xvvx](https://github.com/twisted/twisted/security/advisories/GHSA-92x2-jw7w-xvvx), CVE-2022-21712).

## References
- https://github.com/twisted/treq/security/advisories/GHSA-fhpf-pp6p-55qc
- https://nvd.nist.gov/vuln/detail/CVE-2022-23607
- https://github.com/twisted/treq/commit/1da6022cc880bbcff59321abe02bf8498b89efb2
- https://github.com/pypa/advisory-database/tree/main/vulns/treq/PYSEC-2022-26.yaml
- https://github.com/twisted/treq
- https://github.com/twisted/treq/releases/tag/release-22.1.0
- https://huntr.dev/bounties/3c9204fc-a3d1-4441-8599-924c5f57e7ae/?token=06d930e37046c914bcb037e85cc227dc7b510b475989fc69837566562ba899277d46b0fb4b1e21cdcb6ddc1b7d9b1ded632cf3a3551ecb89afca16a63b34641284b50479d5195bba2ac09b116f3dd4fad27f54404c2de922c05c8c8b744aec27bb4d4d198cb8b3abf479af0c2d5fbaa10412da7922594ac3eb39
- https://lists.debian.org/debian-lts-announce/2022/03/msg00025.html
