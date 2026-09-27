# [M] URL globbing out of bounds read

## Summary
Severity: Medium
Advisory: CURL-CVE-2017-1000101
Aliases: CVE-2017-1000101
Published: 2017-08-09
Source: https://osv.dev/vulnerability/CURL-CVE-2017-1000101
Type: osv

## Details
curl supports "globbing" of URLs, in which a user can pass a numerical range
to have the tool iterate over those numbers to do a sequence of transfers.

In the globbing function that parses the numerical range, there was an
omission that made curl read a byte beyond the end of the URL if given a
carefully crafted, or wrongly written, URL. The URL is stored in a heap
based buffer, so it could then be made to wrongly read something else instead
of crashing.

An example of a URL that triggers the flaw would be
`http://ur%20[0-60000000000000000000`.
