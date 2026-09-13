# [M] wrong reuse of connections

## Summary
Severity: Medium
Advisory: CURL-CVE-2014-0138
Aliases: CVE-2014-0138
Published: 2014-03-26
Source: https://osv.dev/vulnerability/CURL-CVE-2014-0138
Type: osv

## Details
libcurl can in some circumstances reuse the wrong connection when asked to
do transfers using other protocols than HTTP and FTP.

libcurl features a pool of recent connections so that subsequent requests
can reuse an existing connection to avoid overhead.

When reusing a connection a range of criterion must first be met. Due to an
error in the code, a transfer that was initiated by an application could
wrongfully reuse an existing connection to the same server that was
authenticated using different credentials. The existing logic only worked
well enough for HTTP and FTP, while all other network protocols were
silently, but erroneously, assumed to work like HTTP. Protocols that use
connection oriented authentication need a new connection when new
credentials are used.

Affected protocols include: SCP, SFTP, POP3(S), IMAP(S), SMTP(S) and
LDAP(S).

Applications can disable libcurl's reuse of connections and thus mitigate
this problem, by using one of the following libcurl options to alter how
connections are or are not reused: `CURLOPT_FRESH_CONNECT`,
`CURLOPT_MAXCONNECTS` and `CURLMOPT_MAX_HOST_CONNECTIONS` (if using the
curl_multi API).

(This problem is similar to a problem previously reported to NTLM HTTP
connections, named [CVE-2014-0015](CVE-2014-0015.html))
