# [H] Dex discarding TLSconfig and always serves deprecated TLS 1.0/1.1 and insecure ciphers

## Summary
Severity: High
Advisory: GHSA-gr79-9v6v-gc9r
CVE: CVE-2024-23656
CWE: CWE-326
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-01-26
Source: https://github.com/advisories/GHSA-gr79-9v6v-gc9r
Type: github-advisory

## Affected
- Go: `github.com/dexidp/dex` — affected >=2.37.0 <2.38.0
- Go: `github.com/dexidp/dex` — affected >=0 <0.0.0-20240125115555-5bbdb4420254

## Details
### Summary

Dex 2.37.0 is serving HTTPS with insecure TLS 1.0 and TLS 1.1.


### Details
While working on https://github.com/dexidp/dex/issues/2848 and implementing configurable TLS support, I noticed my changes did not have any effect in TLS config, so I started investigating. 

https://github.com/dexidp/dex/blob/70d7a2c7c1bb2646b1a540e49616cbc39622fb83/cmd/dex/serve.go#L425 is seemingly setting TLS 1.2 as minimum version, but the whole tlsConfig is ignored after "TLS cert reloader" was introduced in https://github.com/dexidp/dex/pull/2964. Configured cipher suites are not respected either, as seen on the output.

### PoC
Build Dex, generate certs with `gencert.sh`, modify `config.dev.yaml` to run on https, using generated certs.

```console
issuer: http://127.0.0.1:5556/dex

storage:
  type: sqlite3
  config:
    file: dex.db

web:
  https: 127.0.0.1:5556
  tlsCert: examples/k8s/ssl/cert.pem
  tlsKey: examples/k8s/ssl/key.pem

<rest as default>
```

Run dex `bin/dex serve config.dev.yaml`.

Install `sslyze`, easy to use SSL connection analyzer:

```console
pip3 install sslyze
sslyze 127.0.0.1:5556
```

In Dex 2.37.0, TLS 1.0 and TLS 1.1 are enabled in addition to expected TLS 1.2 and TLS 1.3.
```console
 * TLS 1.0 Cipher Suites:
     Attempted to connect using 80 cipher suites.

     The server accepted the following 6 cipher suites:
        TLS_RSA_WITH_AES_256_CBC_SHA                      256                      
        TLS_RSA_WITH_AES_128_CBC_SHA                      128                      
        TLS_RSA_WITH_3DES_EDE_CBC_SHA                     168                      
        TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA                256       ECDH: prime256v1 (256 bits)
        TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA                128       ECDH: prime256v1 (256 bits)
        TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA               168       ECDH: prime256v1 (256 bits)

     The group of cipher suites supported by the server has the following properties:
       Forward Secrecy                    OK - Supported
       Legacy RC4 Algorithm               OK - Not Supported


 * TLS 1.1 Cipher Suites:
     Attempted to connect using 80 cipher suites.

     The server accepted the following 6 cipher suites:
        TLS_RSA_WITH_AES_256_CBC_SHA                      256                      
        TLS_RSA_WITH_AES_128_CBC_SHA                      128                      
        TLS_RSA_WITH_3DES_EDE_CBC_SHA                     168                      
        TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA                256       ECDH: prime256v1 (256 bits)
        TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA                128       ECDH: prime256v1 (256 bits)
        TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA               168       ECDH: prime256v1 (256 bits)

     The group of cipher suites supported by the server has the following properties:
       Forward Secrecy                    OK - Supported
       Legacy RC4 Algorithm               OK - Not Supported


 * TLS 1.2 Cipher Suites:
     Attempted to connect using 156 cipher suites.

     The server accepted the following 11 cipher suites:
        TLS_RSA_WITH_AES_256_GCM_SHA384                   256                      
        TLS_RSA_WITH_AES_256_CBC_SHA                      256                      
        TLS_RSA_WITH_AES_128_GCM_SHA256                   128                      
        TLS_RSA_WITH_AES_128_CBC_SHA                      128                      
        TLS_RSA_WITH_3DES_EDE_CBC_SHA                     168                      
        TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256       256       ECDH: X25519 (253 bits)
        TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384             256       ECDH: prime256v1 (256 bits)
        TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA                256       ECDH: prime256v1 (256 bits)
        TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256             128       ECDH: prime256v1 (256 bits)
        TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA                128       ECDH: prime256v1 (256 bits)
        TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA               168       ECDH: prime256v1 (256 bits)

     The group of cipher suites supported by the server has the following properties:
       Forward Secrecy                    OK - Supported
       Legacy RC4 Algorithm               OK - Not Supported


 * TLS 1.3 Cipher Suites:
     Attempted to connect using 5 cipher suites.

     The server accepted the following 3 cipher suites:
        TLS_CHACHA20_POLY1305_SHA256                      256       ECDH: X25519 (253 bits)
        TLS_AES_256_GCM_SHA384                            256       ECDH: X25519 (253 bits)
        TLS_AES_128_GCM_SHA256                            128       ECDH: X25519 (253 bits)
```

In Dex 2.36.0, TLS 1.0 and TLS 1.1 are disabled as expected.
```console
 * TLS 1.0 Cipher Suites:
     Attempted to connect using 80 cipher suites; the server rejected all cipher suites.

 * TLS 1.1 Cipher Suites:
     Attempted to connect using 80 cipher suites; the server rejected all cipher suites.

 * TLS 1.2 Cipher Suites:
     Attempted to connect using 156 cipher suites.

     The server accepted the following 5 cipher suites:
        TLS_RSA_WITH_AES_256_GCM_SHA384                   256                      
        TLS_RSA_WITH_AES_128_GCM_SHA256                   128                      
        TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256       256       ECDH: X25519 (253 bits)
        TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384             256       ECDH: prime256v1 (256 bits)
        TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256             128       ECDH: prime256v1 (256 bits)

     The group of cipher suites supported by the server has the following properties:
       Forward Secrecy                    OK - Supported
       Legacy RC4 Algorithm               OK - Not Supported


 * TLS 1.3 Cipher Suites:
     Attempted to connect using 5 cipher suites.

     The server accepted the following 3 cipher suites:
        TLS_CHACHA20_POLY1305_SHA256                      256       ECDH: X25519 (253 bits)
        TLS_AES_256_GCM_SHA384                            256       ECDH: X25519 (253 bits)
```

### Impact
TLS 1.0 and TLS 1.1 connections can be decrypted by the attacker, and hence decrypt the traffic to Dex.

## References
- https://github.com/dexidp/dex/security/advisories/GHSA-gr79-9v6v-gc9r
- https://nvd.nist.gov/vuln/detail/CVE-2024-23656
- https://github.com/dexidp/dex/issues/2848
- https://github.com/dexidp/dex/pull/2964
- https://github.com/dexidp/dex/commit/5bbdb4420254ba73b9c4df4775fe7bdacf233b17
- https://github.com/dexidp/dex
- https://github.com/dexidp/dex/blob/70d7a2c7c1bb2646b1a540e49616cbc39622fb83/cmd/dex/serve.go#L425
