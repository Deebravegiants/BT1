# [M] CRLF injection in httplib2

## Summary
Severity: Medium
Advisory: GHSA-gg84-qgv9-w4pq
CVE: CVE-2020-11078
CWE: CWE-93
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2020-05-20
Source: https://github.com/advisories/GHSA-gg84-qgv9-w4pq
Type: github-advisory

## Affected
- PyPI: `httplib2` — affected >=0 <0.18.0

## Details
### Impact
Attacker controlling unescaped part of uri for `httplib2.Http.request()` could change request headers and body, send additional hidden requests to same server.

Impacts software that uses httplib2 with uri constructed by string concatenation, as opposed to proper urllib building with escaping.

### Patches
Problem has been fixed in 0.18.0
Space, CR, LF characters are now quoted before any use.
This solution should not impact any valid usage of httplib2 library, that is uri constructed by urllib.

### Workarounds
Create URI with `urllib.parse` family functions: `urlencode`, `urlunsplit`.

```diff
user_input = " HTTP/1.1\r\ninjected: attack\r\nignore-http:"
-uri = "https://api.server/?q={}".format(user_input)
+uri = urllib.parse.urlunsplit(("https", "api.server", "/v1", urllib.parse.urlencode({"q": user_input}), ""))
http.request(uri)
```

### References
https://cwe.mitre.org/data/definitions/93.html
https://docs.python.org/3/library/urllib.parse.html

Thanks to Recar https://github.com/Ciyfly for finding vulnerability and discrete notification.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [httplib2](https://github.com/httplib2/httplib2/issues/new)
* Email [current maintainer at 2020-05](mailto:temotor@gmail.com)

## References
- https://github.com/httplib2/httplib2/security/advisories/GHSA-gg84-qgv9-w4pq
- https://nvd.nist.gov/vuln/detail/CVE-2020-11078
- https://github.com/httplib2/httplib2/commit/a1457cc31f3206cf691d11d2bf34e98865873e9e
- https://github.com/httplib2/httplib2
- https://github.com/pypa/advisory-database/tree/main/vulns/httplib2/PYSEC-2020-46.yaml
- https://lists.apache.org/thread.html/r23711190c2e98152cb6f216b95090d5eeb978543bb7e0bad22ce47fc@%3Cissues.beam.apache.org%3E
- https://lists.apache.org/thread.html/r4d35dac106fab979f0db75a07fc4e320ad848b722103e79667ff99e1@%3Cissues.beam.apache.org%3E
- https://lists.apache.org/thread.html/r69a462e690b5f2c3d418a288a2c98ae764d58587bd0b5d6ab141f25f@%3Cissues.beam.apache.org%3E
- https://lists.apache.org/thread.html/r7f364000066748299b331b615ba51c62f55ab5b201ddce9a22d98202@%3Cissues.beam.apache.org%3E
- https://lists.apache.org/thread.html/rad8872fc99f670958c2774e2bf84ee32a3a0562a0c787465cf3dfa23@%3Cissues.beam.apache.org%3E
- https://lists.apache.org/thread.html/rc9eff9572946142b657c900fe63ea4bbd3535911e8d4ce4d08fe4b89@%3Ccommits.allura.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2020/06/msg00000.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IXCX2AWROGWGY5GXR7VN3BKF34A2FO6J
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PZJ3D6JSM7CFZESZZKGUW2VX55BOSOXI
