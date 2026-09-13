# [H] Sensitive data exposure in NATS

## Summary
Severity: High
Advisory: GHSA-82rf-q3pr-4f6p
CVE: CVE-2020-26149
CWE: CWE-522
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-10-08
Source: https://github.com/advisories/GHSA-82rf-q3pr-4f6p
Type: github-advisory

## Affected
- npm: `nats` — affected >=2.0.0-201 <2.0.0-209
- npm: `nats.ws` — affected >=1.0.0-85 <1.0.0-111

## Details
Preview versions of two NPM packages and one Deno package from the NATS project contain an information disclosure flaw, leaking options to the NATS server; for one package, this includes TLS private credentials.

The `_connection_` configuration options in these JavaScript-based implementations were fully serialized and sent to the server in the client's CONNECT message, immediately after TLS establishment.

The nats.js client supports Mutual TLS and the credentials for the TLS client key are included in the connection configuration options; disclosure of the client's TLS private key to the server has been observed.

Most authentication mechanisms are handled after connection, instead of as part of connection, so other authentication mechanisms are unaffected. For clarity: NATS account NKey authentication is NOT affected.

Neither the nats.ws nor the nats.deno clients support Mutual TLS: the affected versions listed below are those where the logic flaw is present. We are including the nats.ws and nats.deno versions out of an abundance of caution, as library maintainers, but rate as minimal the likelihood of applications leaking sensitive data.

### Security impact:

* NPM package nats.js:
+ mainline is unaffected
+ beta branch is vulnerable from 2.0.0-201, fixed in 2.0.0-209

### Logic flaw:

* NPM package nats.ws:
+ status: preview
+ flawed from 1.0.0-85, fixed in 1.0.0-111
* Deno repository https://github.com/nats-io/nats.deno
+ status: preview
+ flawed in all git tags prior to fix
+ fixed with git tag v1.0.0-9

### Impact:

For deployments using TLS client certificates (for mutual TLS), private key material for TLS is leaked from the client application to the server. If the server is untrusted (run by a third party), or if the client application also disables TLS verification (and so the true identity of the server is unverifiable) then authentication credentials are leaked.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-26149
- https://github.com/nats-io/nats.ws/commit/0a37ac2a411ff63f0707cda69a268c5fc4079eb7
- https://github.com/nats-io/nats.deno/compare/v1.0.0-8...v1.0.0-9
- https://github.com/nats-io/nats.ws
- http://www.openwall.com/lists/oss-security/2020/09/30/3
