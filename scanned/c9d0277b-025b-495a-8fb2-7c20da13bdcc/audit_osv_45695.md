# [M] OpenSSL 1.1.1 introduced a rewritten random number generator (RNG)

## Summary
Severity: Medium
Advisory: JLSEC-2026-215
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/JLSEC-2026-215
Type: osv

## Affected
- Julia: `OpenSSL_jll` — affected >=0 <1.1.1+2

## Details
OpenSSL 1.1.1 introduced a rewritten random number generator (RNG). This was intended to include protection in the event of a fork() system call in order to ensure that the parent and child processes did not share the same RNG state. However this protection was not being used in the default case. A partial mitigation for this issue is that the output from a high precision timer is mixed into the RNG state so the likelihood of a parent and child process sharing state is significantly reduced. If an application already calls `OPENSSL_init_crypto()` explicitly using `OPENSSL_INIT_ATFORK` then this problem does not occur at all. Fixed in OpenSSL 1.1.1d (Affected 1.1.1-1.1.1c).

## References
- https://git.openssl.org/gitweb/?p=openssl.git%3Ba=commitdiff%3Bh=1b0fe00e2704b5e20334a16d3c9099d1ba2ef1be
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=1b0fe00e2704b5e20334a16d3c9099d1ba2ef1be
- https://github.com/advisories/GHSA-xmjp-8ccm-cf6h
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GY6SNRJP2S7Y42GIIDO3HXPNMDYN2U3A
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GY6SNRJP2S7Y42GIIDO3HXPNMDYN2U3A/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZN4VVQJ3JDCHGIHV4Y2YTXBYQZ6PWQ7E
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZN4VVQJ3JDCHGIHV4Y2YTXBYQZ6PWQ7E/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GY6SNRJP2S7Y42GIIDO3HXPNMDYN2U3A
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZN4VVQJ3JDCHGIHV4Y2YTXBYQZ6PWQ7E
- https://nvd.nist.gov/vuln/detail/CVE-2019-1549
- https://seclists.org/bugtraq/2019/Oct/1
- https://security.netapp.com/advisory/ntap-20190919-0002
- https://security.netapp.com/advisory/ntap-20190919-0002/
- https://support.f5.com/csp/article/K44070243
- https://support.f5.com/csp/article/K44070243?utm_source=f5support&amp%3Butm_medium=RSS
- https://support.f5.com/csp/article/K44070243?utm_source=f5support&amp;utm_medium=RSS
- https://usn.ubuntu.com/4376-1
- https://usn.ubuntu.com/4376-1/
- https://www.debian.org/security/2019/dsa-4539
- https://www.openssl.org/news/secadv/20190910.txt
