# [M] cookie parser out of boundary memory access

## Summary
Severity: Medium
Advisory: CURL-CVE-2015-3145
Aliases: CVE-2015-3145
Published: 2015-04-22
Source: https://osv.dev/vulnerability/CURL-CVE-2015-3145
Type: osv

## Details
libcurl supports HTTP "cookies" as documented in RFC 6265. Together with each
individual cookie there are several different properties, but for this
vulnerability we focus on the associated "path" element. It tells information
about for which path on a given host the cookie is valid.

The internal libcurl function called `sanitize_cookie_path()` that cleans up
the path element as given to it from a remote site or when read from a file,
did not properly validate the input. If given a path that consisted of a
single double-quote, libcurl would index a newly allocated memory area with
index -1 and assign a zero to it, thus destroying heap memory it was not
supposed to.

At best, this gets unnoticed but can also lead to a crash or worse. We have
not researched further what kind of malicious actions that potentially this
could be used for.

Applications have to explicitly enable cookie parsing in libcurl for this
problem to trigger, and if not enabled libcurl does not hit this problem.
