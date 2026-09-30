# [M] POST following PUT confusion

## Summary
Severity: Medium
Advisory: CURL-CVE-2022-32221
Aliases: CVE-2022-32221
Published: 2022-10-26
Source: https://osv.dev/vulnerability/CURL-CVE-2022-32221
Type: osv

## Details
When doing HTTP(S) transfers, libcurl might erroneously use the read callback
(`CURLOPT_READFUNCTION`) to ask for data to send, even when the
`CURLOPT_POSTFIELDS` option has been set, if the same handle previously was
used to issue a `PUT` request which used that callback.

This flaw may surprise the application and cause it to misbehave and either
send off the wrong data or use memory after free or similar in the subsequent
`POST` request.

The problem exists in the logic for a reused handle when it is changed from a
PUT to a POST.
