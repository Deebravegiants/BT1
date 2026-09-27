# [H] uninitialized random

## Summary
Severity: High
Advisory: CURL-CVE-2016-9594
Aliases: CVE-2016-9594
Published: 2016-12-23
Source: https://osv.dev/vulnerability/CURL-CVE-2016-9594
Type: osv

## Details
libcurl's (new) internal function that returns a good 32-bit random value was
implemented poorly and overwrote the pointer instead of writing the value into
the buffer the pointer pointed to.

This random value is used to generate nonces for Digest and NTLM
authentication, for generating boundary strings in HTTP formposts and
more. Having a weak or virtually non-existent random there makes these
operations vulnerable.

This function is brand new in 7.52.0 and is the result of an overhaul to make
sure libcurl uses strong random as much as possible - provided by the backend
TLS crypto libraries when present.
