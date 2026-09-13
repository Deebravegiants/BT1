# [M] Inferior OCSP verification

## Summary
Severity: Medium
Advisory: CURL-CVE-2020-8286
Aliases: CVE-2020-8286
Published: 2020-12-09
Source: https://osv.dev/vulnerability/CURL-CVE-2020-8286
Type: osv

## Details
libcurl offers "OCSP stapling" via the `CURLOPT_SSL_VERIFYSTATUS` option. When
set, libcurl verifies the OCSP response that a server responds with as part of
the TLS handshake. It then aborts the TLS negotiation if something is wrong
with the response. The same feature can be enabled with `--cert-status` using
the curl tool.

As part of the OCSP response verification, a client should verify that the
response is indeed set out for the correct certificate. This step was not
performed by libcurl when built or told to use OpenSSL as TLS backend.

This flaw would allow an attacker, who perhaps could have breached a TLS
server, to provide a fraudulent OCSP response that would appear fine, instead
of the real one. Like if the original certificate actually has been revoked.
