# [C] CVE-2020-11945

## Summary
Severity: Critical
Advisory: CVE-2020-11945
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-23
Source: https://osv.dev/vulnerability/CVE-2020-11945
Type: osv

## Details
An issue was discovered in Squid before 5.0.2. A remote attacker can replay a sniffed Digest Authentication nonce to gain access to resources that are otherwise forbidden. This occurs because the attacker can overflow the nonce reference counter (a short integer). Remote code execution may occur if the pooled token credentials are freed (instead of replayed as valid credentials).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4FWQRYZJPHAZBLXJ56FPCHJN5X2FP3VA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/H4MWXEZAJSOGRJSS2JCJK4WBSND4IV46/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RV2VZWFJNO3B56IVN56HHKJASG5DYUIX/
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00018.html
- http://master.squid-cache.org/Versions/v4/changesets/squid-4-eeebf0f37a72a2de08348e85ae34b02c34e9a811.patch
- http://www.openwall.com/lists/oss-security/2020/04/23/2
- https://lists.debian.org/debian-lts-announce/2020/07/msg00009.html
- https://security.gentoo.org/glsa/202005-05
- https://security.netapp.com/advisory/ntap-20210304-0004/
- https://usn.ubuntu.com/4356-1/
- https://www.debian.org/security/2020/dsa-4682
- https://bugzilla.suse.com/show_bug.cgi?id=1170313
- http://www.squid-cache.org/Versions/v4/changesets/squid-4-eeebf0f37a72a2de08348e85ae34b02c34e9a811.patch
- https://github.com/squid-cache/squid/commit/eeebf0f37a72a2de08348e85ae34b02c34e9a811
- https://github.com/squid-cache/squid/pull/585
