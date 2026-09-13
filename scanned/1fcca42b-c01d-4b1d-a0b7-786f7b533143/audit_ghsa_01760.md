# [C] Local file inclusion vulnerability in http4s

## Summary
Severity: Critical
Advisory: GHSA-66q9-f7ff-mmx6
CVE: CVE-2020-5280
CWE: CWE-23
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2020-03-25
Source: https://github.com/advisories/GHSA-66q9-f7ff-mmx6
Type: github-advisory

## Affected
- Maven: `org.http4s:http4s-server_2.12` — affected >=0 <0.18.26
- Maven: `org.http4s:http4s-server_2.12` — affected >=0.19.0 <0.20.20
- Maven: `org.http4s:http4s-server_2.12` — affected >=0.21.0 <0.21.2

## Details
### Impact

This vulnerability applies to all users of:
* `org.http4s.server.staticcontent.FileService`
* `org.http4s.server.staticcontent.ResourceService`
* `org.http4s.server.staticcontent.WebjarService`

#### Path escaping

URI normalization is applied incorrectly.  Requests whose path info contain `../` or `//` can expose resources outside of the configured location.  Specifically:

* `FileService` may expose any file on the local file system.
* `ResourceService` may expose any resource on the class path.

#### Prefix matching

When the service is configured with a non-empty `pathPrefix` that doesn't end in a slash, any directories whose names are a prefix of `systemPath` (from `FileService`) or `pathPrefix` (from `ResourceService`) are exposed.  For example, if `pathPrefix` is `/foo` and `systemPath` is `/bar`, a request to `/foobaz/quux.txt` exposes file `/barbaz/quux.txt`, when only files beneath `/bar` should be available.

#### URI decoding

URI segments are not decoded before resource resolution.  This causes resources with reserved characters in their name to incorrectly return a 404.  It also may incorrectly expose the rare resource whose name is URI encoded.  This applies to `FileService`, `ResourceService`, and `WebjarService`.

### Patches

In all three services, paths with an empty segment, a `.` segment, or a `..` segment are now rejected with a `400 Bad Request` response.  This fixes exposure outside the configured root.  Many clients already eliminate dot segments according to the rules in [RFC3986, Section 5.2.4](https://tools.ietf.org/html/rfc3986#section-5.2.4).  A middleware that does so at the server level may be considered if there is demand.

If `pathInfo` is non-empty, and does not begin with `/`, then a 404 response is generated.  This fixes the prefix matching exposure.

All path segments are URI decoded before being passed to the file system or resource path.  This allows resolution of resources with reserved characters in the name, and prevents incorrect exposure of resources whose names are themselves URI encoded.

### Workarounds

The recommended course is to upgrade:
* v0.18.26, binary compatible with the 0.18.x series
* v0.20.20, binary compatible with the 0.20.x series
* v0.21.2, binary compatible with the 0.21.x series

Note that 0.19.0 is a deprecated release and has never been supported.

If an upgrade is impossible:

* Temporarily copy `FileService.scala`, `ResourceService.scala`, and `WebjarService.scala` from the appropriate release series into your project and recompile with that, changing the package name and reference in your application.
* Users of a servlet backend can use the servlet container's file serving capabilities.

### Credits

Thank you to Thomas Gøytil for the discovery, responsible disclosure, and assistance testing of this vulnerability.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [http4s/http4s](http://github.com/http4s/http4s)
* Email a maintainer:
  * [Ross A. Baker](mailto:ross@rossabaker.com)

## References
- https://github.com/http4s/http4s/security/advisories/GHSA-66q9-f7ff-mmx6
- https://nvd.nist.gov/vuln/detail/CVE-2020-5280
- https://github.com/http4s/http4s/commit/250afddbb2e65b70ca9ddaec9d1eb3aaa56de7ec
- https://github.com/http4s/http4s/commit/752b3f63a05a31d2de4f8706877aa08d6b89efca
- https://github.com/http4s/http4s/commit/b87f31b2292dabe667bec3b04ce66176c8a3e17b
