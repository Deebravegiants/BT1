# [M] There is an overflow bug in the `x64_64` Montgomery squaring procedure used in exponentiation with...

## Summary
Severity: Medium
Advisory: JLSEC-2026-216
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/JLSEC-2026-216
Type: osv

## Affected
- Julia: `OpenSSL_jll` — affected >=0 <1.1.1+2
- Julia: `Openresty_jll` — affected >=0 <1.19.9+0

## Details
There is an overflow bug in the `x64_64` Montgomery squaring procedure used in exponentiation with 512-bit moduli. No EC algorithms are affected. Analysis suggests that attacks against 2-prime RSA1024, 3-prime RSA1536, and DSA1024 as a result of this defect would be very difficult to perform and are not believed likely. Attacks against DH512 are considered just feasible. However, for an attack the target would have to re-use the DH512 private key, which is not recommended anyway. Also applications directly using the low level API `BN_mod_exp` may be affected if they use `BN_FLG_CONSTTIME`. Fixed in OpenSSL 1.1.1e-dev (Affected 1.1.1-1.1.1d). Fixed in OpenSSL 1.0.2u-dev (Affected 1.0.2-1.0.2t).

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00030.html
- http://packetstormsecurity.com/files/155754/Slackware-Security-Advisory-openssl-Updates.html
- https://git.openssl.org/gitweb/?p=openssl.git%3Ba=commitdiff%3Bh=419102400a2811582a7a3d4a4e317d72e5ce0a8f
- https://git.openssl.org/gitweb/?p=openssl.git%3Ba=commitdiff%3Bh=f1c5eea8a817075d31e43f5876993c6710238c98
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=419102400a2811582a7a3d4a4e317d72e5ce0a8f
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=f1c5eea8a817075d31e43f5876993c6710238c98
- https://github.com/advisories/GHSA-fcc6-m5v9-xcgq
- https://lists.debian.org/debian-lts-announce/2022/03/msg00023.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DDHOAATPWJCXRNFMJ2SASDBBNU5RJONY
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DDHOAATPWJCXRNFMJ2SASDBBNU5RJONY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EXDDAOWSAIEFQNBHWYE6PPYFV4QXGMCD
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EXDDAOWSAIEFQNBHWYE6PPYFV4QXGMCD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XVEP3LAK4JSPRXFO4QF4GG2IVXADV3SO
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XVEP3LAK4JSPRXFO4QF4GG2IVXADV3SO/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DDHOAATPWJCXRNFMJ2SASDBBNU5RJONY
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/EXDDAOWSAIEFQNBHWYE6PPYFV4QXGMCD
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XVEP3LAK4JSPRXFO4QF4GG2IVXADV3SO
- https://nvd.nist.gov/vuln/detail/CVE-2019-1551
- https://seclists.org/bugtraq/2019/Dec/39
- https://seclists.org/bugtraq/2019/Dec/46
