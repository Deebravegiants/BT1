# [M] CVE-2016-1938

## Summary
Severity: Medium
Advisory: CVE-2016-1938
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2016-01-31
Source: https://osv.dev/vulnerability/CVE-2016-1938
Type: osv

## Details
The s_mp_div function in lib/freebl/mpi/mpi.c in Mozilla Network Security Services (NSS) before 3.21, as used in Mozilla Firefox before 44.0, improperly divides numbers, which might make it easier for remote attackers to defeat cryptographic protection mechanisms by leveraging use of the (1) mp_div or (2) mp_exptmod function.

## References
- https://github.com/hannob/bignum-fuzz/blob/master/CVE-2016-1938-nss-mp_div.c
- https://github.com/hannob/bignum-fuzz/blob/master/CVE-2016-1938-nss-mp_exptmod.c
- https://hg.mozilla.org/projects/nss/diff/a555bf0fc23a/lib/freebl/mpi/mpi.c
- http://www.securitytracker.com/id/1034825
- http://lists.opensuse.org/opensuse-security-announce/2016-02/msg00010.html
- http://www.securityfocus.com/bid/81955
- https://developer.mozilla.org/en-US/docs/Mozilla/Projects/NSS/NSS_3.21_release_notes
- https://security.gentoo.org/glsa/201605-06
- http://www.ubuntu.com/usn/USN-2903-1
- http://lists.opensuse.org/opensuse-security-announce/2016-02/msg00001.html
- http://www.mozilla.org/security/announce/2016/mfsa2016-07.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2016-2881720.html
- http://www.ubuntu.com/usn/USN-2880-1
- https://security.gentoo.org/glsa/201701-46
- http://www.ubuntu.com/usn/USN-2973-1
- http://lists.opensuse.org/opensuse-security-announce/2016-02/msg00002.html
- http://www.debian.org/security/2016/dsa-3688
- http://www.securityfocus.com/bid/91787
- http://www.ubuntu.com/usn/USN-2880-2
- http://www.ubuntu.com/usn/USN-2903-2
