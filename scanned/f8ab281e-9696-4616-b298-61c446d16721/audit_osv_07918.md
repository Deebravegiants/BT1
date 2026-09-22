# [M] HTTP proxy double free

## Summary
Severity: Medium
Advisory: CURL-CVE-2022-42915
Aliases: CVE-2022-42915
Published: 2022-10-26
Source: https://osv.dev/vulnerability/CURL-CVE-2022-42915
Type: osv

## Details
If curl is told to use an HTTP proxy for a transfer with a non-HTTP(S) URL, it
sets up the connection to the remote server by issuing a `CONNECT` request to
the proxy, and then *tunnels* the rest of protocol through.

An HTTP proxy might refuse this request (HTTP proxies often only allow
outgoing connections to specific port numbers, like 443 for HTTPS) and instead
return a non-200 response code to the client.

Due to flaws in the error/cleanup handling, this could trigger a double free
in curl if one of the following schemes were used in the URL for the transfer:
`dict`, `gopher`, `gophers`, `ldap`, `ldaps`, `rtmp`, `rtmps`, `telnet`
