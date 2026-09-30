# [M] Protocol downgrade required TLS bypassed

## Summary
Severity: Medium
Advisory: CURL-CVE-2021-22946
Aliases: CVE-2021-22946
Published: 2021-09-15
Source: https://osv.dev/vulnerability/CURL-CVE-2021-22946
Type: osv

## Details
A user can tell curl to **require** a successful upgrade to TLS when speaking
to an IMAP, POP3 or FTP server (`--ssl-reqd` on the command line or
`CURLOPT_USE_SSL` set to `CURLUSESSL_CONTROL` or `CURLUSESSL_ALL` with
libcurl). This requirement could be bypassed if the server would return a
properly crafted but perfectly legitimate response.

This flaw would then make curl silently continue its operations **without
TLS** contrary to the instructions and expectations, exposing possibly
sensitive data in clear text over the network.
