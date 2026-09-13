# [H] Response Splitting from unsanitized headers

## Summary
Severity: High
Advisory: GHSA-5vcm-3xc3-w7x3
CVE: CVE-2021-41084
CWE: CWE-74, CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2021-09-22
Source: https://github.com/advisories/GHSA-5vcm-3xc3-w7x3
Type: github-advisory

## Affected
- Maven: `org.http4s:http4s-client_2.12` — affected >=0 <0.21.29
- Maven: `org.http4s:http4s-client_2.12` — affected >=0.22.0 <0.22.5
- Maven: `org.http4s:http4s-client_2.12` — affected >=0.23.0 <0.23.4
- Maven: `org.http4s:http4s-client_2.13` — affected >=0 <0.21.29
- Maven: `org.http4s:http4s-client_2.13` — affected >=0.22.0 <0.22.5
- Maven: `org.http4s:http4s-client_2.13` — affected >=0.23.0 <0.23.4
- Maven: `org.http4s:http4s-client_3` — affected >=0 <0.21.29
- Maven: `org.http4s:http4s-client_3` — affected >=0.22.0 <0.22.5
- Maven: `org.http4s:http4s-client_3` — affected >=0.23.0 <0.23.4
- Maven: `org.http4s:http4s-server_2.10` — affected >=0
- Maven: `org.http4s:http4s-server_2.11` — affected >=0
- Maven: `org.http4s:http4s-server_2.12` — affected >=0 <0.21.29
- Maven: `org.http4s:http4s-server_2.12` — affected >=0.22.0 <0.22.5
- Maven: `org.http4s:http4s-server_2.12` — affected >=0.23.0 <0.23.4
- Maven: `org.http4s:http4s-server_2.13` — affected >=0 <0.21.29
- Maven: `org.http4s:http4s-server_2.13` — affected >=0.22.0 <0.22.5
- Maven: `org.http4s:http4s-server_2.13` — affected >=0.23.0 <0.23.4
- Maven: `org.http4s:http4s-server_2.13.0-M5` — affected >=0
- Maven: `org.http4s:http4s-server_3` — affected >=0.22.0 <0.22.5
- Maven: `org.http4s:http4s-server_3` — affected >=0.23.0 <0.23.4

## Details
### Impact

http4s is vulnerable to response-splitting or request-splitting attacks when untrusted user input is used to create any of the following fields:

* Header names (`Header.name`å
* Header values (`Header.value`)
* Status reason phrases (`Status.reason`)
* URI paths (`Uri.Path`)
* URI authority registered names (`URI.RegName`) (through 0.21)

The following backends render invalid carriage return, newline, or null characters in an unsafe fashion.

|                | blaze-server | ember-server | blaze-client | ember-client | jetty-client |
|:---------------|:-------------|:-------------|:-------------|--------------|--------------|
| header names   | ⚠            | ⚠            | ⚠            | ⚠            |   ⚠            | 
| header values  | ⚠            | ⚠            | ⚠            | ⚠            |              |
| status reasons | ⚠            | ⚠            |              |              |              |
| URI paths      |              |              |  ⚠             |  ⚠             |              |
| URI regnames   |              |              |  ⚠ < 0.22           |  ⚠ < 0.22            |              |

For example, given the following service:

```scala
import cats.effect._
import org.http4s._
import org.http4s.dsl.io._
import org.http4s.server.blaze.BlazeServerBuilder
import scala.concurrent.ExecutionContext.global

object ResponseSplit extends IOApp {
  override def run(args: List[String]): IO[ExitCode] =
    BlazeServerBuilder[IO](global)
      .bindHttp(8080)
      .withHttpApp(httpApp)
      .resource
      .use(_ => IO.never)

  val httpApp: HttpApp[IO] =
    HttpApp[IO] { req =>
      req.params.get("author") match {
        case Some(author) =>
          Ok("The real content")
            .map(_.putHeaders(Header("Set-Cookie", s"author=${author}")))
        case None =>
          BadRequest("No author parameter")
      }
    }
}
```

A clean `author` parameter returns a clean response:

```sh
curl -i 'http://localhost:8080/?author=Ross'
```

```http
HTTP/1.1 200 OK
Content-Type: text/plain; charset=UTF-8
Set-Cookie: author=Ross
Date: Mon, 20 Sep 2021 04:12:10 GMT
Content-Length: 16

The real content
```

A malicious `author` parameter allows a user-agent to hijack the response from our server and return different content:

```sh
curl -i 'http://localhost:8080/?author=hax0r%0d%0aContent-Length:+13%0d%0a%0aI+hacked+you'
```

```http
HTTP/1.1 200 OK
Content-Type: text/plain; charset=UTF-8
Set-Cookie: author=hax0r
Content-Length: 13

I hacked you
```

### Patches

Versions 0.21.29, 0.22.5, 0.23.4, and 1.0.0-M27 perform the following:

* If a status reasoon phrase is invalid, it is dropped. Rendering is optional per spec.
* If a header name is invalid in a request or response, the header is dropped.  There is no way to generically sanitize a header without potentially shadowing a correct one.
* If a header value is invalid in a request or response, it is sanitized by replacing null (`\u0000`), carriage return (`\r`), and newline (`\n`) with space (` `) characters per spec.
* If a URI path or registered name is invalid in a request line, the client raises an `IllegalArgumentException`.
* If a URI registered name is invalid in a host header, the client raises an `IllegalArgumentException`. 

### Workarounds

http4s services and client applications should sanitize any user input in the aforementioned fields before returning a request or response to the backend.  The carriage return, newline, and null characters are the most threatening.

Not all backends were affected: jetty-server, tomcat-server, armeria, and netty on the server; async-http-client, okhttp-client, armeria, and netty as clients.

### References
* https://owasp.org/www-community/attacks/HTTP_Response_Splitting
* https://httpwg.org/http-core/draft-ietf-httpbis-semantics-latest.html#fields.values

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [GitHub](http://github.com/http4s/http4s)
* Contact us via the [http4s security policy](https://github.com/http4s/http4s/security/policy)

## References
- https://github.com/http4s/http4s/security/advisories/GHSA-5vcm-3xc3-w7x3
- https://nvd.nist.gov/vuln/detail/CVE-2021-41084
- https://github.com/http4s/http4s/commit/d02007db1da4f8f3df2dbf11f1db9ac7afc3f9d8
- https://github.com/http4s/http4s
- https://httpwg.org/http-core/draft-ietf-httpbis-semantics-latest.html#fields.values
- https://owasp.org/www-community/attacks/HTTP_Response_Splitting
