# [H] URL request injection

## Summary
Severity: High
Advisory: CURL-CVE-2014-8150
Aliases: CVE-2014-8150
Published: 2015-01-08
Source: https://osv.dev/vulnerability/CURL-CVE-2014-8150
Type: osv

## Details
When libcurl sends a request to a server via an HTTP proxy, it copies the
entire URL into the request and sends if off.

If the given URL contains line feeds and carriage returns those are sent along
to the proxy too, which allows the program to for example send a separate HTTP
request injected embedded in the URL.

Many programs allow some kind of external sources to set the URL or provide
partial pieces for the URL to ask for, and if the URL as received from the
user is not stripped good enough this flaw allows malicious users to do
additional requests in a way that was not intended, or to insert request
headers into the request that the program did not intend.
