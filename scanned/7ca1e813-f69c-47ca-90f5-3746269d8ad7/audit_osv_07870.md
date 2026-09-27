# [H] sensitive HTTP server headers also sent to proxies

## Summary
Severity: High
Advisory: CURL-CVE-2015-3153
Aliases: CVE-2015-3153
Published: 2015-04-29
Source: https://osv.dev/vulnerability/CURL-CVE-2015-3153
Type: osv

## Details
libcurl provides applications a way to set custom HTTP headers to be sent to
the server by using `CURLOPT_HTTPHEADER`. A similar option is available for
the curl command-line tool with the '--header' option.

When the connection passes through an HTTP proxy the same set of headers is
sent to the proxy as well by default. While this is by design, it has not
necessarily been clear nor understood by application programmers.

Such tunneling over a proxy is done for example when using the HTTPS protocol
- or when explicitly asked for. In this case, the initial connection to the
proxy is made in clear including any custom headers using the HTTP CONNECT
method.

While libcurl provides the `CURLOPT_HEADEROPT` option to allow applications to
tell libcurl if the headers should be sent to host and the proxy or use
separate lists to the different destinations, it has still defaulted to
sending the same headers to both parties for the sake of compatibility.

If the application sets a custom HTTP header with sensitive content (e.g.,
authentication cookies) without changing the default, the proxy, and anyone
who listens to the traffic between the application and the proxy, might get
access to those values.

Note: this problem does not exist when using the `CURLOPT_COOKIE` option (or
the `--cookie` option) or the HTTP auth options, which are always sent only to
the destination server.
