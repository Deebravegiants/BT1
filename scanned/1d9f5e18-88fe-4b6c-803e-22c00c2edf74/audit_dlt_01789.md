# [?] Adjust OpenSSL defaults and mitigate CVE-2021-3499:

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2021-03-30
Source: https://github.com/XRPLF/rippled/commit/79e69da3647019840dca49622621c3d88bc3883f
Type: security-commit

## Details
Adjust OpenSSL defaults and mitigate CVE-2021-3499:

In order to effectively mitigate CVE-2021-3499 even when compiling
against versions of OpenSSL prior to 1.1.1k, this commit:

1) requires use of TLS 1.2 or later. Note that both TLS 1.0 and
   TLS 1.1 have been officially deprecated for over a year.
2) disables renegotiation support for TLS 1.2 connections.

Lastly, this commit also changes the default list of ciphers that
the server offers, limiting it only to ciphers that are part of
TLS 1.2.
