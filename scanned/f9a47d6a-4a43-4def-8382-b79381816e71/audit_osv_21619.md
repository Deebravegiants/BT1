# [C] CVE-2021-44538

## Summary
Severity: Critical
Advisory: CVE-2021-44538
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-12-14
Source: https://osv.dev/vulnerability/CVE-2021-44538
Type: osv

## Details
The olm_session_describe function in Matrix libolm before 3.2.7 is vulnerable to a buffer overflow. The Olm session object represents a cryptographic channel between two parties. Therefore, its state is partially controllable by the remote party of the channel. Attackers can construct a crafted sequence of messages to manipulate the state of the receiver's session in such a way that, for some buffer sizes, a buffer overflow happens on a call to olm_session_describe. Furthermore, safe buffer sizes were undocumented. The overflow content is partially controllable by the attacker and limited to ASCII spaces and digits. The known affected products are Element Web And SchildiChat Web.

## References
- https://gitlab.matrix.org/matrix-org/olm/-/tags
- https://lists.debian.org/debian-lts-announce/2022/01/msg00001.html
- https://www.debian.org/security/2022/dsa-5034
- https://matrix.org/blog/2021/12/13/disclosure-buffer-overflow-in-libolm-and-matrix-js-sdk
