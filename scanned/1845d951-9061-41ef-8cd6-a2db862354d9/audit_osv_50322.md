# [C] CVE-2020-12403

## Summary
Severity: Critical
Advisory: CVE-2020-12403
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2021-05-27
Source: https://osv.dev/vulnerability/CVE-2020-12403
Type: osv

## Details
A flaw was found in the way CHACHA20-POLY1305 was implemented in NSS in versions before 3.55. When using multi-part Chacha20, it could cause out-of-bounds reads. This issue was fixed by explicitly disabling multi-part ChaCha20 (which was not functioning correctly) and strictly enforcing tag length. The highest threat from this vulnerability is to confidentiality and system availability.

## References
- https://lists.debian.org/debian-lts-announce/2023/02/msg00021.html
- https://developer.mozilla.org/en-US/docs/Mozilla/Projects/NSS/NSS_3.55_release_notes
- https://security.netapp.com/advisory/ntap-20230324-0006/
- https://bugzilla.redhat.com/show_bug.cgi?id=1868931
