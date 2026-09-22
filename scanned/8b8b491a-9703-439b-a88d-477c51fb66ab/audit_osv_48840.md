# [M] CVE-2018-15599

## Summary
Severity: Medium
Advisory: CVE-2018-15599
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2018-08-21
Source: https://osv.dev/vulnerability/CVE-2018-15599
Type: osv

## Details
The recv_msg_userauth_request function in svr-auth.c in Dropbear through 2018.76 is prone to a user enumeration vulnerability because username validity affects how fields in SSH_MSG_USERAUTH messages are handled, a similar issue to CVE-2018-15473 in an unrelated codebase.

## References
- https://matt.ucc.asn.au/dropbear/CHANGES
- http://lists.ucc.gu.uwa.edu.au/pipermail/dropbear/2018q3/002108.html
- http://lists.ucc.gu.uwa.edu.au/pipermail/dropbear/2018q3/002109.html
- https://lists.debian.org/debian-lts-announce/2018/08/msg00026.html
- https://old.reddit.com/r/blackhat/comments/97ywnm/openssh_username_enumeration/e4e05n2/
