# [H] CVE-2017-17818

## Summary
Severity: High
Advisory: CVE-2017-17818
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-12-21
Source: https://osv.dev/vulnerability/CVE-2017-17818
Type: osv

## Details
In Netwide Assembler (NASM) 2.14rc0, there is a heap-based buffer over-read that will cause a remote denial of service attack, related to a while loop in paste_tokens in asm/preproc.c.

## References
- https://usn.ubuntu.com/3694-1/
- https://bugzilla.nasm.us/show_bug.cgi?id=3392428
