# [H] double free in krb5 code

## Summary
Severity: High
Advisory: CURL-CVE-2016-8619
Aliases: CVE-2016-8619
Published: 2016-11-02
Source: https://osv.dev/vulnerability/CURL-CVE-2016-8619
Type: osv

## Details
In curl's implementation of the Kerberos authentication mechanism, the
function `read_data()` in security.c is used to fill the necessary krb5
structures. When reading one of the length fields from the socket, it fails to
ensure that the length parameter passed to realloc() is not set to 0.

This would lead to realloc() getting called with a zero size and when doing so
realloc() returns NULL *and* frees the memory - in contrary to normal
realloc() fails where it only returns NULL - causing libcurl to free the
memory *again* in the error path.

This flaw could be triggered by a malicious or otherwise ill-behaving server.
