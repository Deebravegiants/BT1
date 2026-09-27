# [M] Hash collision in typelevel jawn

## Summary
Severity: Medium
Advisory: GHSA-vc89-hccf-rq55
CVE: CVE-2022-21653
CWE: CWE-326, CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-vc89-hccf-rq55
Type: github-advisory

## Affected
- Maven: `org.typelevel:jawn-parser_0.25` — affected >=0
- Maven: `org.typelevel:jawn-parserg` — affected >=0
- Maven: `org.typelevel:jawn-parser_0.27` — affected >=0
- Maven: `org.typelevel:jawn-parser_2.10` — affected >=0
- Maven: `org.typelevel:jawn-parser_2.11` — affected >=0
- Maven: `org.typelevel:jawn-parser_2.12` — affected >=0 <1.3.2
- Maven: `org.typelevel:jawn-parser_2.13` — affected >=0 <1.3.2
- Maven: `org.typelevel:jawn-parser_2.13.0-M5` — affected >=0
- Maven: `org.typelevel:jawn-parser_2.13.0-RC1` — affected >=0
- Maven: `org.typelevel:jawn-parser_2.13.0-RC2` — affected >=0
- Maven: `org.typelevel:jawn-parser_2.13.0-RC3` — affected >=0
- Maven: `org.typelevel:jawn-parser_3` — affected >=0 <1.3.2
- Maven: `org.typelevel:jawn-parser_3.0.0-M1` — affected >=0
- Maven: `org.typelevel:jawn-parser_3.0.0-M2` — affected >=0
- Maven: `org.typelevel:jawn-parser_3.0.0-M3` — affected >=0
- Maven: `org.typelevel:jawn-parser_3.0.0-RC1` — affected >=0
- Maven: `org.typelevel:jawn-parser_3.0.0-RC2` — affected >=0
- Maven: `org.typelevel:jawn-parser_3.0.0-RC3` — affected >=0

## Details
### Impact

Extenders of the `org.typelevel.jawn.SimpleFacade` and `org.typelevel.jawn.MutableFacade` who don't override `objectContext()` are vulnerable to a hash collision attack.  Most applications do not implement these traits directly, but inherit from a library:

Affected implementations include:
* `org.http4s` :: `http4s-play-json`
* `org.typelevel :: jawn-ast` (< 0.8.0)
* `org.typelevel :: jawn-play` (discontinued)
* `org.typelevel :: jawn-rojoma` (discontinued)
* `org.typelevel :: jawn-spray` (discontinued)

Unaffected implementations include:
* `io.argonaut :: argonaut-jawn`
* `io.circe :: circe-parser`
* `org.typelevel :: jawn-ast` (>= 0.8.0)
* `org.typelevel :: jawn-json4s` (discontinued)
* `org.typelevel :: jawn-argonaut` (discontinued)

### Patches

`jawn-parser-1.3.2` fixes the issue.

### Workarounds

Override `objectContext()` to use a collision-safe collection.  See [the patch](https://github.com/typelevel/jawn/pull/390/files) for an example in both `SimpleFacade` and `MutableFacade`.

### References

* https://github.com/typelevel/jawn/pull/390

### Credits

* @kag0, for the report and the patch

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [typelevel/jawn](https://github.com/typelevel/jawn)
* E-mail a maintainer:
  * [@rossabaker](mailto:ross@rossabaker.com)

## References
- https://github.com/typelevel/jawn/security/advisories/GHSA-vc89-hccf-rq55
- https://nvd.nist.gov/vuln/detail/CVE-2022-21653
- https://github.com/typelevel/jawn/pull/390
- https://github.com/typelevel/jawn
