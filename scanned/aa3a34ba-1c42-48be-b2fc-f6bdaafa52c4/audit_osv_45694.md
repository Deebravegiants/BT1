# [M] Normally in OpenSSL EC groups always have a co-factor present and this is used in side channel...

## Summary
Severity: Medium
Advisory: JLSEC-2026-214
Ecosystem: Julia
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/JLSEC-2026-214
Type: osv

## Affected
- Julia: `OpenSSL_jll` — affected >=0 <1.1.1+2

## Details
Normally in OpenSSL EC groups always have a co-factor present and this is used in side channel resistant code paths. However, in some cases, it is possible to construct a group using explicit parameters (instead of using a named curve). In those cases it is possible that such a group does not have the cofactor present. This can occur even where all the parameters match a known named curve. If such a curve is used then OpenSSL falls back to non-side channel resistant code paths which may result in full key recovery during an ECDSA signature operation. In order to be vulnerable an attacker would have to have the ability to time the creation of a large number of signatures where explicit parameters with no co-factor present are in use by an application using libcrypto. For the avoidance of doubt libssl is not vulnerable because explicit parameters are never used. Fixed in OpenSSL 1.1.1d (Affected 1.1.1-1.1.1c). Fixed in OpenSSL 1.1.0l (Affected 1.1.0-1.1.0k). Fixed in OpenSSL 1.0.2t (Affected 1.0.2-1.0.2s).

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00054.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00072.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00016.html
- http://packetstormsecurity.com/files/154467/Slackware-Security-Advisory-openssl-Updates.html
- https://arxiv.org/abs/1909.01785
- https://git.openssl.org/gitweb/?p=openssl.git%3Ba=commitdiff%3Bh=21c856b75d81eff61aa63b4f036bb64a85bf6d46
- https://git.openssl.org/gitweb/?p=openssl.git%3Ba=commitdiff%3Bh=30c22fa8b1d840036b8e203585738df62a03cec8
- https://git.openssl.org/gitweb/?p=openssl.git%3Ba=commitdiff%3Bh=7c1709c2da5414f5b6133d00a03fc8c5bf996c7a
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=21c856b75d81eff61aa63b4f036bb64a85bf6d46
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=30c22fa8b1d840036b8e203585738df62a03cec8
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=7c1709c2da5414f5b6133d00a03fc8c5bf996c7a
- https://github.com/advisories/GHSA-q2qv-648h-wcqp
- https://kc.mcafee.com/corporate/index?page=content&id=SB10365
- https://lists.debian.org/debian-lts-announce/2019/09/msg00026.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GY6SNRJP2S7Y42GIIDO3HXPNMDYN2U3A
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GY6SNRJP2S7Y42GIIDO3HXPNMDYN2U3A/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZN4VVQJ3JDCHGIHV4Y2YTXBYQZ6PWQ7E
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZN4VVQJ3JDCHGIHV4Y2YTXBYQZ6PWQ7E/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GY6SNRJP2S7Y42GIIDO3HXPNMDYN2U3A
