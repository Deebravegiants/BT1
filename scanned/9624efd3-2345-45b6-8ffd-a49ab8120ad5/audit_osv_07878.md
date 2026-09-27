# [M] URL unescape heap overflow via integer truncation

## Summary
Severity: Medium
Advisory: CURL-CVE-2016-8622
Aliases: CVE-2016-8622
Published: 2016-11-02
Source: https://osv.dev/vulnerability/CURL-CVE-2016-8622
Type: osv

## Details
The URL percent-encoding decode function in libcurl is called
`curl_easy_unescape`. Internally, even if this function would be made to
allocate a destination buffer larger than 2GB, it would return that new length
in a signed 32-bit integer variable, thus the length would get either
truncated only or both truncated and turned negative. That could then lead
to libcurl writing outside of its heap based buffer.

This can be triggered by a user on a 64-bit system if the user can send in a
custom (large) URL to a libcurl using program.
