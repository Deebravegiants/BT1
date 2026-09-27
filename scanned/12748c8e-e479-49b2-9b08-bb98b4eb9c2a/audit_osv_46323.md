# [H] embedded zero in cert name

## Summary
Severity: High
Advisory: CURL-CVE-2009-2417
Aliases: CVE-2009-2417
Published: 2009-08-12
Source: https://osv.dev/vulnerability/CURL-CVE-2009-2417
Type: osv

## Details
SSL and TLS Server certificates contain one or more fields with server name
or otherwise matching patterns. These strings are stored as content and
length within the certificate, and thus there is no particular terminating
character.

curl's OpenSSL interfacing code did faulty assumptions about those names and
patterns being null-terminated, allowing itself to be fooled in case a
certificate would get a zero byte embedded into one of the name fields. To
illustrate, a name that would show this vulnerability could look like:

  "example.com\0.haxx.se"

This cert is thus made for "haxx.se" but curl would erroneously verify it
with no complaints for "example.com".

According to a recently published presentation, this kind of zero embedding
has been proven to be possible with at least one CA.
