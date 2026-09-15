# [H] CVE-2017-10686

## Summary
Severity: High
Advisory: CVE-2017-10686
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-06-29
Source: https://osv.dev/vulnerability/CVE-2017-10686
Type: osv

## Details
In Netwide Assembler (NASM) 2.14rc0, there are multiple heap use after free vulnerabilities in the tool nasm. The related heap is allocated in the token() function and freed in the detoken() function (called by pp_getline()) - it is used again at multiple positions later that could cause multiple damages. For example, it causes a corrupted double-linked list in detoken(), a double free or corruption in delete_Token(), and an out-of-bounds write in detoken(). It has a high possibility to lead to a remote code execution attack.

## References
- https://security.gentoo.org/glsa/201903-19
- https://usn.ubuntu.com/3694-1/
- https://bugzilla.nasm.us/show_bug.cgi?id=3392414
