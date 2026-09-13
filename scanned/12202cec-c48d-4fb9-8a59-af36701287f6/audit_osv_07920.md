# [M] UAF in SSH sha256 fingerprint check

## Summary
Severity: Medium
Advisory: CURL-CVE-2023-28319
Aliases: CVE-2023-28319
Published: 2023-05-17
Source: https://osv.dev/vulnerability/CURL-CVE-2023-28319
Type: osv

## Details
libcurl offers a feature to verify an SSH server's public key using a SHA 256
hash. When this check fails, libcurl would free the memory for the fingerprint
before it returns an error message containing the (now freed) hash.

This flaw risks inserting sensitive heap-based data into the error message
that might be shown to users or otherwise get leaked and revealed.
