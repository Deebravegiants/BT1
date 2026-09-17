# [H] cookie domain tailmatch

## Summary
Severity: High
Advisory: CURL-CVE-2013-1944
Aliases: CVE-2013-1944
Published: 2013-04-12
Source: https://osv.dev/vulnerability/CURL-CVE-2013-1944
Type: osv

## Details
libcurl is vulnerable to a cookie leak vulnerability when doing requests
  across domains with matching tails.

  When communicating over HTTP(S) and having libcurl's cookie engine enabled,
  libcurl stores and holds cookies for use when subsequent requests are done
  to hosts and paths that match those kept cookies. Due to a bug in the
  tailmatching function, libcurl could wrongly send cookies meant for the
  domain 'ample.com' when communicating with 'example.com'.

  This vulnerability can be used to hijack sessions in targeted attacks since
  registering domains using a known domain's name as an ending is trivial.

  Both curl the command line tool and applications using the libcurl library
  are vulnerable.
