# [M] CVE-2019-16930

## Summary
Severity: Medium
Advisory: CVE-2019-16930
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-09-28
Source: https://osv.dev/vulnerability/CVE-2019-16930
Type: osv

## Details
Zcashd in Zcash before 2.0.7-3 allows discovery of the IP address of a full node that owns a shielded address, related to mishandling of exceptions during deserialization of note plaintexts. This affects anyone who has disclosed their zaddr to a third party.

## References
- http://duke.leto.net/2019/10/01/zcash-metadata-leakage-cve-2019-16930.html
- https://github.com/zcash/zcash/releases/tag/v2.0.7-3
- https://z.cash/support/security/announcements/security-announcement-2019-09-24/
- https://github.com/zcash/zcash/commit/c1fbf8ab5d73cff5e1f45236995857c75ba4128d
