# [H] cookie leak for TLDs

## Summary
Severity: High
Advisory: CURL-CVE-2014-3620
Aliases: CVE-2014-3620
Published: 2014-09-10
Source: https://osv.dev/vulnerability/CURL-CVE-2014-3620
Type: osv

## Details
libcurl wrongly allows cookies to be set for Top Level Domains (TLDs), thus
making them apply broader than cookies are allowed. This can allow arbitrary
sites to set cookies that then would get sent to a different and unrelated
site or domain.
