# [H] CVE-2017-7468

## Summary
Severity: High
Advisory: CVE-2017-7468
Aliases: CURL-CVE-2017-7468
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-07-16
Source: https://osv.dev/vulnerability/CVE-2017-7468
Type: osv

## Details
In curl and libcurl 7.52.0 to and including 7.53.1, libcurl would attempt to resume a TLS session even if the client certificate had changed. That is unacceptable since a server by specification is allowed to skip the client certificate check on resume, and may instead use the old identity which was established by the previous certificate (or no certificate). libcurl supports by default the use of TLS session id/ticket to resume previous TLS sessions to speed up subsequent TLS handshakes. They are used when for any reason an existing TLS connection couldn't be kept alive to make the next handshake faster. This flaw is a regression and identical to CVE-2016-5419 reported on August 3rd 2016, but affecting a different version range.

## References
- http://www.securityfocus.com/bid/97962
- http://www.securitytracker.com/id/1038341
- https://curl.haxx.se/docs/adv_20170419.html
- https://security.gentoo.org/glsa/201709-14
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-7468
