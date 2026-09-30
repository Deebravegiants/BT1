# [M] freeing stack buffer in utf8asn1str

## Summary
Severity: Medium
Advisory: CURL-CVE-2024-6197
Aliases: CVE-2024-6197
Published: 2024-07-24
Source: https://osv.dev/vulnerability/CURL-CVE-2024-6197
Type: osv

## Details
libcurl's ASN1 parser has this `utf8asn1str()` function used for parsing an
ASN.1 UTF-8 string. It can detect an invalid field and return error.
Unfortunately, when doing so it also invokes `free()` on a 4 byte local stack
buffer.

Most modern malloc implementations detect this error and immediately abort.
Some however accept the input pointer and add that memory to its list of
available chunks. This leads to the overwriting of nearby stack memory. The
content of the overwrite is decided by the `free()` implementation; likely to
be memory pointers and a set of flags.

The most likely outcome of exploiting this flaw is a crash, although it cannot
be ruled out that more serious results can be had in special circumstances.
