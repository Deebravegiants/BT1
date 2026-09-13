# [M] StaticFile.fromUrl can leak presence of a directory

## Summary
Severity: Medium
Advisory: GHSA-6h7w-fc84-x7p6
CVE: CVE-2021-32643
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2021-05-28
Source: https://github.com/advisories/GHSA-6h7w-fc84-x7p6
Type: github-advisory

## Affected
- Maven: `org.http4s:http4s-core` — affected >=0.21.7 <0.21.24
- Maven: `org.http4s:http4s-core` — affected >=0.22.0-M1 <0.22.0-RC1
- Maven: `org.http4s:http4s-core` — affected >=0.23.0-M1 <0.23.0-RC1
- Maven: `org.http4s:http4s-core` — affected >=1.0.0-M1 <1.0.0-M23

## Details
### Impact

`StaticFile.fromUrl` can leak the presence of a directory on a server when the `URL` scheme is not `file://`, and the URL points to a fetchable resource under its scheme and authority.  The function returns `F[None]`, indicating no resource, if `url.getFile` is a directory, without first checking the scheme or authority of the URL.  If a URL connection to the scheme and URL would return a stream, and the path in the URL exists as a directory on the server, the presence of the directory on the server could be inferred from the 404 response.  The contents and other metadata about the directory are not exposed.

This affects http4s versions:
* 0.21.7 through 0.21.23
* 0.22.0-M1 through 0.22.0-M8
* 0.23.0-M1
* 1.0.0-M1 through 1.0.0-M22

### Patches

The [patch](https://github.com/http4s/http4s/commit/52e1890665410b4385e37b96bc49c5e3c708e4e9) is available in the following versions:

* v0.21.24
* v0.22.0-RC1
* v0.23.0-RC1
* v1.0.0-M23

Note: a previous version of this advisory incorrectly referred to 0.22.0-M9 and 0.23.0-M2.

### Workarounds

Don't call `StaticFile.fromUrl` with non-file URLs.

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [the http4s repository](https://github.com/http4s/http4s)
* Disclose further vulnerabilities according to the [http4s security policy](https://github.com/http4s/http4s/blob/main/SECURITY.md)

## References
- https://github.com/http4s/http4s/security/advisories/GHSA-6h7w-fc84-x7p6
- https://nvd.nist.gov/vuln/detail/CVE-2021-32643
- https://github.com/http4s/http4s/commit/52e1890665410b4385e37b96bc49c5e3c708e4e9
- https://mvnrepository.com/artifact/org.http4s/http4s-core
