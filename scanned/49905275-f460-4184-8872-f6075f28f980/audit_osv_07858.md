# [H] data callback excessive length

## Summary
Severity: High
Advisory: CURL-CVE-2010-0734
Aliases: CVE-2010-0734
Published: 2010-02-09
Source: https://osv.dev/vulnerability/CURL-CVE-2010-0734
Type: osv

## Details
When downloading data, libcurl hands it over to the application using a
callback that is registered by the client software. libcurl then calls that
function repeatedly with data until the transfer is complete. The callback is
documented to receive a maximum data size of 16K (`CURL_MAX_WRITE_SIZE`).

Using the affected libcurl version to download compressed content over HTTP,
an application can ask libcurl to automatically uncompress data. When doing
so, libcurl can wrongly send data up to 64K in size to the callback which
thus is much larger than the documented maximum size. An application that
blindly trusts libcurl's max limit for a fixed buffer size or similar is
then a possible target for a buffer overflow vulnerability.

This error is only present in zlib-enabled builds of libcurl and only if
automatic decompression has been explicitly enabled by the application - it
is disabled by default.

We have not found any libcurl client software that is vulnerable to this
flaw - but we acknowledge that there may still be vulnerable software in
existence.
