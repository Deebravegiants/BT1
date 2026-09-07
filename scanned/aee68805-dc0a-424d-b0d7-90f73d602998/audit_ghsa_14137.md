# [M] Kyverno vulnerable due to usage of insecure cipher

## Summary
Severity: Medium
Advisory: GHSA-hgv6-w7r3-w4qw
Ecosystem: Go
Published: 2023-05-30
Source: https://github.com/advisories/GHSA-hgv6-w7r3-w4qw
Type: github-advisory

## Affected
- Go: `github.com/kyverno/kyverno` — affected >=0 <1.9.5

## Details
### Summary
Insecure 3DES ciphers are used which may lead to exploitation of the [Sweet32 vulnerability](https://sweet32.info/). Specifically, the ciphers TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA (secp256r1) and TLS_RSA_WITH_3DES_EDE_CBC_SHA (rsa 2048) are allowed. See CVE-2016-2183. This is fixed in Kyverno v1.9.5 and v1.10.0 and no known users have been affected.

### Details

The ciphers in affected versions can be read using the following command which uses `nmap`:

```sh
$ kubectl exec -it mypod -n kyverno sh 
kubectl exec [POD] [COMMAND] is DEPRECATED and will be removed in a future version. Use kubectl exec [POD] -- [COMMAND] instead.
**nmap -sV --script ssl-enum-ciphers -p 443 kyverno-cleanup-controller** or  
**nmap -sV --script ssl-enum-ciphers -p 443 kyverno-svc**
Starting Nmap 7.92 ( https://nmap.org ) at 2023-05-26 10:55 UTC
Nmap scan report for kyverno-cleanup-controller (10.103.199.233)
Host is up (0.000058s latency).
rDNS record for 10.103.199.233: kyverno-cleanup-controller.kyverno.svc.cluster.local

PORT    STATE SERVICE  VERSION
443/tcp open  ssl/http Golang net/http server (Go-IPFS json-rpc or InfluxDB API)
| ssl-enum-ciphers: 
|   TLSv1.2: 
|     ciphers: 
**|       TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA (secp256r1) - C**
|       TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA (secp256r1) - A
|       TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 (secp256r1) - A
|       TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA (secp256r1) - A
|       TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 (secp256r1) - A
|       TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256 (secp256r1) - A
**|       TLS_RSA_WITH_3DES_EDE_CBC_SHA (rsa 2048) - C**
|       TLS_RSA_WITH_AES_128_CBC_SHA (rsa 2048) - A
|       TLS_RSA_WITH_AES_128_GCM_SHA256 (rsa 2048) - A
|       TLS_RSA_WITH_AES_256_CBC_SHA (rsa 2048) - A
|       TLS_RSA_WITH_AES_256_GCM_SHA384 (rsa 2048) - A
|     compressors: 
|       NULL
|     cipher preference: client
|     warnings: 
|       64-bit block cipher 3DES vulnerable to SWEET32 attack
|   TLSv1.3: 
|     ciphers: 
|       TLS_AKE_WITH_AES_128_GCM_SHA256 (ecdh_x25519) - A
|       TLS_AKE_WITH_AES_256_GCM_SHA384 (ecdh_x25519) - A
|       TLS_AKE_WITH_CHACHA20_POLY1305_SHA256 (ecdh_x25519) - A
|     cipher preference: server
|_  least strength: C

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 12.72 seconds
```

## References
- https://github.com/kyverno/kyverno/security/advisories/GHSA-hgv6-w7r3-w4qw
- https://github.com/kyverno/kyverno/pull/7308
- https://github.com/kyverno/kyverno
- https://github.com/kyverno/kyverno/releases/tag/v1.9.5
