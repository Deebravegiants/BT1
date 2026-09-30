# [M] CVE-2017-15955

## Summary
Severity: Medium
Advisory: CVE-2017-15955
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-10-28
Source: https://osv.dev/vulnerability/CVE-2017-15955
Type: osv

## Details
bchunk (related to BinChunker) 1.2.0 and 1.2.1 is vulnerable to an "Access violation near NULL on destination operand" and crash when processing a malformed CUE (.cue) file.

## References
- https://lists.debian.org/debian-lts-announce/2017/11/msg00001.html
- https://www.debian.org/security/2017/dsa-4026
- https://github.com/hessu/bchunk/issues/2
- https://github.com/extramaster/bchunk/issues/4
