# [M] inappropriate GSSAPI delegation

## Summary
Severity: Medium
Advisory: CURL-CVE-2011-2192
Aliases: CVE-2011-2192
Published: 2011-06-23
Source: https://osv.dev/vulnerability/CURL-CVE-2011-2192
Type: osv

## Details
When doing GSSAPI authentication, libcurl unconditionally performs
credential delegation. This hands the server a copy of the client's security
credentials, allowing the server to impersonate the client to any other
using the same GSSAPI mechanism. This is obviously a sensitive operation,
which should only be done when the user explicitly so directs.

The GSS/Negotiate feature is only used by libcurl for HTTP authentication if
told to, and only if libcurl was built with a library that provides the
GSSAPI. Many builds of libcurl do not have GSS enabled.
