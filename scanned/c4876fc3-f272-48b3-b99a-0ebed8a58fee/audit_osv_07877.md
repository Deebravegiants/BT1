# [M] curl_getdate read out of bounds

## Summary
Severity: Medium
Advisory: CURL-CVE-2016-8621
Aliases: CVE-2016-8621
Published: 2016-11-02
Source: https://osv.dev/vulnerability/CURL-CVE-2016-8621
Type: osv

## Details
The `curl_getdate` converts a given date string into a numerical timestamp and
it supports a range of different formats and possibilities to express a date
and time. The underlying date parsing function is also used internally when
parsing for example HTTP cookies (possibly received from remote servers) and
it can be used when doing conditional HTTP requests.

The date parser function uses the libc `sscanf()` function at two places, with
the parsing strings `%02d:%02d` and `%02d:%02d:%02d`. The intent being that it
would parse either a string with HH:MM (two digits colon two digits) or
`HH:MM:SS` (two digits colon two digits colon two digits). If instead the
piece of time that was sent in had the final digit cut off, thus ending with a
single-digit, the date parser code would advance its read pointer one byte too
much and end up reading out of bounds.
