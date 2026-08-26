# [C] Silent omission of certificate hostname verification in LibreSSL and BoringSSL

## Summary
Severity: Critical (CVSS 9.1)
Program: Internet Bug Bounty
Weakness: Improper Certificate Validation
Reporter: tiran
State: resolved
Disclosed: 2019-09-26T20:38:28.174Z
CVE: CVE-2018-8970
Source: https://hackerone.com/reports/329645

## Details
## Abstract

LibreSSL and BoringSSL implemented ``X509_VERIFY_PARAM_set1_host`` differently than OpenSSL. All applications that use the preferred and documented way to configure a TLS connection for hostname validation, silently neglect to perform hostname validation at all. As a consequence, they are vulnerable to MitM attacks.

## Description

OpenSSL 1.0.2 introduced the function [X509_VERIFY_PARAM_set1_host](https://www.openssl.org/docs/man1.0.2/crypto/X509_VERIFY_PARAM_set1_host.html). It sets the expected DNS hostname for a TLS connection. During the handshake, OpenSSL verifies, that the hostname matches one of the DNS names in the subject alternative name extension of the server's X.509 certificate. It's a critical step to authenticate the identity of a TLS server. A client **must** properly validate the server's DNS name.

The ``X509_VERIFY_PARAM_set1_host`` function takes three parameters. The second parameter is the expected host name, the third parameter is the length of the host name. OpenSSL allows the caller to pass in ``0`` as namelen. It indicates that the server name is a NULL terminated C string. It's documented in the man page for the function and used as example on OpenSSL's [wiki page](https://wiki.openssl.org/index.php/Hostname_validation) about hostname validation. The wiki page is the top hit for a Google search for "openssl hostname validation".

LibreSSL and BoringSSL implement the same function. LibreSSL release 2.7.0 added ``X509_VERIFY_PARAM_set1_host`` just a few days ago. However both libraries behave differently in very subtle but critical way. Their implementation of ``X509_VERIFY_PARAM_set1_host(param, "hostname", 0)`` does **not** configure the TLS/SSL connection to validate the hostname. Instead the call only clears any previously configured hostname and returns success. As a consequence, LibreSSL and BoringSSL do **not** perform any hostname validation and except just any arbitrary certificate for any hostname as long as the certificate is generally trusted. Since the function call returns success, the application never sees an error, too.

The man page for LibreSSL 2.7.0 even documented to support the calling convention. The release took the divergent implementation from BoringSSL but the documentation from OpenSSL.

## Demo

The attached files and https://github.com/tiran/CVE-2018-8970 are a demo for the bug. WIth OpenSSL the command fails as expected with a hostname mismatch error:

```
$ make
...
Error connecting to server
140678245971584:error:1416F086:SSL routines:tls_process_server_certificate:certificate verify failed:ssl/statem/statem_clnt.c:1230:
X509 verify error: Hostname mismatch
```

With LibreSSL 2.7.0 the command does not fail

```
$ make SSL_BASEDIR=/path/to/libressl/2.7.0
...
./cve2018_8970_demo
HTTP/1.1 200 OK
Server: nginx
Content-Type: text/plain
X-Frame-Options: SAMEORIGIN
x-xss-protection: 1; mode=block
X-Clacks-Overhead: GNU Terry Pratchett
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/329645_
