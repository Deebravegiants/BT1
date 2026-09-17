# [H] Http4s improperly parses User-Agent and Server headers

## Summary
Severity: High
Advisory: GHSA-54w6-vxfh-fw7f
CVE: CVE-2023-22465
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-01-06
Source: https://github.com/advisories/GHSA-54w6-vxfh-fw7f
Type: github-advisory

## Affected
- Maven: `org.http4s:http4s-core_2.13` — affected >=0.1.0 <0.21.34
- Maven: `org.http4s:http4s-core_2.13` — affected >=0.22.0 <0.22.15
- Maven: `org.http4s:http4s-core_2.13` — affected >=0.23.0 <0.23.17
- Maven: `org.http4s:http4s-core_2.13` — affected >=1.0.0-M1 <1.0.0-M38
- Maven: `org.http4s:http4s-core_2.10` — affected >=0.1.0
- Maven: `org.http4s:http4s-core_2.11` — affected >=0.1.0
- Maven: `org.http4s:http4s-core_2.12` — affected >=0.1.0 <0.21.34
- Maven: `org.http4s:http4s-core_2.12` — affected >=0.22.0 <0.22.15
- Maven: `org.http4s:http4s-core_2.12` — affected >=0.23.0 <0.23.17
- Maven: `org.http4s:http4s-core` — affected >=1.0.0-M1

## Details
### Impact

The `User-Agent` and `Server` header parsers are susceptible to a fatal error on certain inputs.  In http4s, modeled headers are lazily parsed, so this only applies to services that explicitly request these typed headers. 

#### v0.21.x

```scala
val unsafe: Option[`User-Agent`] = req.headers.get(`User-Agent`)
```

#### v0.22.x, v0.23.x, v1.x

```scala
val unsafe: Option[`User-Agent`] = req.headers.get[`User-Agent`]
val alsoUnsafe: Option[`Server`] = req.headers.get[Server]
```

### Patches

Fixes are released in 0.21.34, 0.22.15, 0.23.17, and 1.0.0-M38.

### Workarounds

#### Use the weakly typed header interface

##### v0.21.x

```scala
val safe: Option[Header] = req.headers.get("User-Agent".ci)
// but don't do this
val unsafe = header.map(_.parsed) 
```

##### v0.22.x, v0.23.x, v1.x

```scala
val safe: Option[Header] = req.headers.get(ci"User-Agent")
```

## References
- https://github.com/http4s/http4s/security/advisories/GHSA-54w6-vxfh-fw7f
- https://nvd.nist.gov/vuln/detail/CVE-2023-22465
- https://github.com/http4s/http4s
