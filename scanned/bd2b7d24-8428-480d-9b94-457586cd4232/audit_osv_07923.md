# [M] cookie mixed case PSL bypass

## Summary
Severity: Medium
Advisory: CURL-CVE-2023-46218
Aliases: CVE-2023-46218
Published: 2023-12-06
Source: https://osv.dev/vulnerability/CURL-CVE-2023-46218
Type: osv

## Details
This flaw allows a malicious HTTP server to set "super cookies" in curl that
are then passed back to more origins than what is otherwise allowed or
possible. This allows a site to set cookies that then would get sent to
different and unrelated sites and domains.

It could do this by exploiting a mixed case flaw in curl's function that
verifies a given cookie domain against the Public Suffix List (PSL). For
example a cookie could be set with `domain=co.UK` when the URL used a
lowercase hostname `curl.co.uk`, even though `co.uk` is listed as a PSL
domain.
