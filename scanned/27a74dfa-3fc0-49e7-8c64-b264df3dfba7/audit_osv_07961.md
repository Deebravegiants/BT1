# [M] CVE-2016-0702

## Summary
Severity: Medium
Advisory: CVE-2016-0702
CVSS: 5.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-03-03
Source: https://osv.dev/vulnerability/CVE-2016-0702
Type: osv

## Details
The MOD_EXP_CTIME_COPY_FROM_PREBUF function in crypto/bn/bn_exp.c in OpenSSL 1.0.1 before 1.0.1s and 1.0.2 before 1.0.2g does not properly consider cache-bank access times during modular exponentiation, which makes it easier for local users to discover RSA keys by running a crafted application on the same Intel Sandy Bridge CPU core as a victim and leveraging cache-bank conflicts, aka a "CacheBleed" attack.

## References
- http://cachebleed.info
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- https://git.openssl.org/?p=openssl.git%3Ba=commit%3Bh=708dc2f1291e104fe4eef810bb8ffc1fae5b19c1
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10759
- http://lists.fedoraproject.org/pipermail/package-announce/2016-March/178358.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-March/178817.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00002.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00003.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00004.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00005.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00007.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00009.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00025.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00038.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00017.html
