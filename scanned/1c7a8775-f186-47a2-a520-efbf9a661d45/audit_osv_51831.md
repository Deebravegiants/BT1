# [H] CVE-2021-4156

## Summary
Severity: High
Advisory: CVE-2021-4156
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2022-03-23
Source: https://osv.dev/vulnerability/CVE-2021-4156
Type: osv

## Details
An out-of-bounds read flaw was found in libsndfile's FLAC codec functionality. An attacker who is able to submit a specially crafted file (via tricking a user to open or otherwise) to an application linked with libsndfile and using the FLAC codec, could trigger an out-of-bounds read that would most likely cause a crash but could potentially leak memory information that could be used in further exploitation of other flaws.

## References
- https://lists.debian.org/debian-lts-announce/2025/12/msg00013.html
- https://security.gentoo.org/glsa/202309-11
- https://lists.debian.org/debian-lts-announce/2022/06/msg00020.html
- https://lists.debian.org/debian-lts-announce/2022/09/msg00036.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2027690
- https://github.com/libsndfile/libsndfile/issues/731
- https://github.com/libsndfile/libsndfile/pull/732/commits/4c30646abf7834e406f7e2429c70bc254e18beab
