# [M] Traefik routes exposed with an empty TLSOption

## Summary
Severity: Medium
Advisory: GHSA-468w-8x39-gj5v
CVE: CVE-2022-46153
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-12-08
Source: https://github.com/advisories/GHSA-468w-8x39-gj5v
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.9.6

## Details
## Impact

There is a potential vulnerability in Traefik managing the TLS connections.

A router configured with a not well-formatted [TLSOption](https://doc.traefik.io/traefik/v2.9/https/tls/#tls-options) is exposed with an empty TLSOption.

For instance, a route secured using an mTLS connection set with a wrong CA file is exposed without verifying the client certificates.

## Patches

https://github.com/traefik/traefik/releases/tag/v2.9.6

## Workarounds

Check the logs to detect the following error messages and fix your TLS options:

- Empty CA:

```
{"level":"error","msg":"invalid clientAuthType: RequireAndVerifyClientCert, CAFiles is required","routerName":"Router0@file"}
```

- Bad CA content (or bad path):

```
{"level":"error","msg":"invalid certificate(s) content","routerName":"Router0@file"}
```

- Unknown Client Auth Type:

```
{"level":"error","msg":"unknown client auth type \"FooClientAuthType\"","routerName":"Router0@file"}
```

- Invalid cipherSuites

```
{"level":"error","msg":"invalid CipherSuite: foobar","routerName":"Router0@file"}
```

- Invalid curvePreferences

```
{"level":"error","msg":"invalid CurveID in curvePreferences: foobar","routerName":"Router0@file"}
``` 

## For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-468w-8x39-gj5v
- https://nvd.nist.gov/vuln/detail/CVE-2022-46153
- https://github.com/traefik/traefik/commit/7e3fe48b80083b41e9ff82a474a36484cabc701a
- https://doc.traefik.io/traefik/v2.9/https/tls/#tls-options
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.9.6
