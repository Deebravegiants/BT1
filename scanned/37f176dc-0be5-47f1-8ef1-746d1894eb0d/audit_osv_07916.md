# [M] Credential leak on redirect

## Summary
Severity: Medium
Advisory: CURL-CVE-2022-27774
Aliases: CVE-2022-27774
Published: 2022-04-27
Source: https://osv.dev/vulnerability/CURL-CVE-2022-27774
Type: osv

## Details
curl follows HTTP(S) redirects when asked to. curl also supports
authentication. When a user and password are provided for a URL with a given
hostname, curl makes an effort to not pass on those credentials to other hosts
in redirects unless given permission with a special option.

This "same host check" has been flawed all since it was introduced. It does
not work on cross protocol redirects and it does not consider different port
numbers to be separate hosts. This leads to curl leaking credentials to other
servers when it follows redirects from auth protected HTTP(S) URLs to other
protocols and port numbers. It could also leak the TLS SRP credentials this
way.

By default, curl only allows redirects to HTTP(S) and FTP(S), but can be asked
to allow redirects to all protocols curl supports.
