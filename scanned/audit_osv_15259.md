# [C] CVE-2019-14842

## Summary
Severity: Critical
Advisory: CVE-2019-14842
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-26
Source: https://osv.dev/vulnerability/CVE-2019-14842
Type: osv

## Details
Structured reply is a feature of the newstyle NBD protocol allowing the server to send a reply in chunks. A bounds check which was supposed to test for chunk offsets smaller than the beginning of the request did not work because of signed/unsigned confusion. If one of these chunks contains a negative offset then data under control of the server is written to memory before the read buffer supplied by the client. If the read buffer is located on the stack then this allows the stack return address from nbd_pread() to be trivially modified, allowing arbitrary code execution under the control of the server. If the buffer is located on the heap then other memory objects before the buffer can be overwritten, which again would usually lead to arbitrary code execution.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14842
- https://www.redhat.com/archives/libguestfs/2019-October/msg00060.html
