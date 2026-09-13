# [H] Use after free via shared cookies

## Summary
Severity: High
Advisory: CURL-CVE-2016-8623
Aliases: CVE-2016-8623
Published: 2016-11-02
Source: https://osv.dev/vulnerability/CURL-CVE-2016-8623
Type: osv

## Details
libcurl explicitly allows users to share cookies between multiple easy handles
that are concurrently employed by different threads.

When cookies to be sent to a server are collected, the matching function
collects all cookies to send and the cookie lock is released immediately
afterwards. That function however only returns a list with *references* back
to the original strings for name, value, path and so on. Therefore, if another
thread quickly takes the lock and frees one of the original cookie structs
together with its strings, a use after free can occur and lead to information
disclosure. Another thread can also replace the contents of the cookies from
separate HTTP responses or API calls.
