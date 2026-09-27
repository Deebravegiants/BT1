# [M] token leak with redirect and netrc

## Summary
Severity: Medium
Advisory: CURL-CVE-2026-3783
Aliases: CVE-2026-3783
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CURL-CVE-2026-3783
Type: osv

## Details
When an OAuth2 bearer token is used for an HTTP(S) transfer, and that transfer
performs a redirect to a second URL, curl could leak that token to the second
hostname under some circumstances.

If the hostname that the first request is redirected to has information in the
used .netrc file, with either of the `machine` or `default` keywords, curl
would pass on the bearer token set for the first host also to the second one.
