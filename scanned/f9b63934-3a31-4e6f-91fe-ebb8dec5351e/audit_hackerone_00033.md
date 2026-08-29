# [M] CVE-2025-4947: QUIC certificate check skip with wolfSSL

## Summary
Severity: Medium
Program: curl
Weakness: Improper Validation of Certificate with Host Mismatch
Reporter: kurohiro
State: resolved
Disclosed: 2025-05-28T06:35:36.415Z
CVE: CVE-2025-4947
Source: https://hackerone.com/reports/3150884

## Details
## Summary:
When using WolfSSL as the TLS backend, there is an issue where the CN or SAN in the certificate is not verified when connecting to an IP address over HTTP/3.

wolfSSL_X509_check_host is only called when `peer->sni` is not NULL.
However, when an IP address is specified, `peer->sni` is NULL, so the verification does not occur.

Curl_vquic_tls_verify_peer()
```
#elif defined(USE_WOLFSSL)
  (void)data;
  if(conn_config->verifyhost) {
    if(peer->sni) {
      WOLFSSL_X509* cert = wolfSSL_get_peer_certificate(ctx->wssl.ssl);
      if(wolfSSL_X509_check_host(cert, peer->sni, strlen(peer->sni), 0, NULL)
            == WOLFSSL_FAILURE) {
        result = CURLE_PEER_FAILED_VERIFICATION;
      }
      wolfSSL_X509_free(cert);
    }

  }
#endif
```

## Affected version
```
curl -V
WARNING: this libcurl is Debug-enabled, do not use in production

curl 8.13.0 (x86_64-pc-linux-gnu) libcurl/8.13.0 wolfSSL/5.8.0 zlib/1.3.1 libidn2/2.3.8 libpsl/0.21.2 ngtcp2/1.13.0-DEV nghttp3/1.1
Release-Date: 2025-04-02
Protocols: dict file ftp ftps gopher gophers http https imap imaps ipfs ipns mqtt pop3 pop3s rtsp smtp smtps telnet tftp ws wss
Features: alt-svc AsynchDNS Debug HSTS HTTP3 HTTPS-proxy IDN IPv6 Largefile libz PSL SSL threadsafe TrackMemory UnixSockets
```

## Steps To Reproduce:
I will explain using a connection to google.com as an example.


_Trimmed to 38 lines — full report: https://hackerone.com/reports/3150884_
