# [H] JLSEC-2026-58

## Summary
Severity: High
Advisory: JLSEC-2026-58
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/JLSEC-2026-58
Type: osv

## Affected
- Julia: `ICU_jll` — affected >=0 <67.1.0+3

## Details
An issue was discovered in International Components for Unicode (ICU) for C/C++ through 66.1. An integer overflow, leading to a heap-based buffer overflow, exists in the UnicodeString::doAppend() function in `common/unistr.cpp`.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00004.html
- https://access.redhat.com/errata/RHSA-2020:0738
- https://bugs.chromium.org/p/chromium/issues/detail?id=1044570
- https://chromereleases.googleblog.com/2020/02/stable-channel-update-for-desktop_24.html
- https://chromium.googlesource.com/chromium/deps/icu/+/9f4020916eb1f28f3666f018fdcbe6c9a37f0e08
- https://github.com/unicode-org/icu/commit/b7d08bc04a4296982fcef8b6b8a354a9e4e7afca
- https://github.com/unicode-org/icu/pull/971
- https://lists.debian.org/debian-lts-announce/2020/03/msg00024.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4OOYAMJVLLCLXDTHW3V5UXNULZBBK4O6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6IOHSO6BUKC6I66J5PZOMAGFVJ66ZS57/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/X3B5RWJQD5LA45MYLLR55KZJOJ5NVZGP/
- https://security.gentoo.org/glsa/202003-15
- https://unicode-org.atlassian.net/browse/ICU-20958
- https://usn.ubuntu.com/4305-1/
- https://www.debian.org/security/2020/dsa-4646
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujan2021.html
