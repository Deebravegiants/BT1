# [H] Proxy Authentication Header Information Leakage

## Summary
Severity: High
Advisory: CURL-CVE-2003-1605
Aliases: CVE-2003-1605
Published: 2003-08-03
Source: https://osv.dev/vulnerability/CURL-CVE-2003-1605
Type: osv

## Details
When curl connected to a site via an HTTP proxy with the CONNECT request, the
user and password used for the proxy connection was also sent off to the
remote server.
