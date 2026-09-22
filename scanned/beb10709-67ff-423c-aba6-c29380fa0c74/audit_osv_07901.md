# [M] NTLM type-2 out-of-bounds buffer read

## Summary
Severity: Medium
Advisory: CURL-CVE-2018-16890
Aliases: CVE-2018-16890
Published: 2019-02-06
Source: https://osv.dev/vulnerability/CURL-CVE-2018-16890
Type: osv

## Details
libcurl contains a heap buffer out-of-bounds read flaw.

The function handling incoming NTLM type-2 messages
(`lib/vauth/ntlm.c:ntlm_decode_type2_target`) does not validate incoming data
correctly and is subject to an integer overflow vulnerability.

Using that overflow, a malicious or broken NTLM server could trick libcurl to
accept a bad length + offset combination that would lead to a buffer read
out-of-bounds.
