# [M] OOB write via unchecked multiplication

## Summary
Severity: Medium
Advisory: CURL-CVE-2016-8617
Aliases: CVE-2016-8617
Published: 2016-11-02
Source: https://osv.dev/vulnerability/CURL-CVE-2016-8617
Type: osv

## Details
In libcurl's base64 encode function, the output buffer is allocated as follows
without any checks on `insize`:

    malloc( insize * 4 / 3 + 4 )

On systems with 32-bit addresses in userspace (e.g. x86, ARM, x32), the
multiplication in the expression wraps around if `insize` is at least 1GB of
data. If this happens, an undersized output buffer is allocated, but the full
result is written, thus causing the memory behind the output buffer to be
overwritten.

If a username is set directly via `CURLOPT_USERNAME` (or curl's `-u, --user`
option), this vulnerability can be triggered. The name has to be at least
512MB big in a 32-bit system.

Systems with 64-bit versions of the `size_t` type are not affected by this
issue.
