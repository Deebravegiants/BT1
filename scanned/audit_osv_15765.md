# [M] CVE-2019-19480

## Summary
Severity: Medium
Advisory: CVE-2019-19480
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-01
Source: https://osv.dev/vulnerability/CVE-2019-19480
Type: osv

## Details
An issue was discovered in OpenSC through 0.19.0 and 0.20.x through 0.20.0-rc3. libopensc/pkcs15-prkey.c has an incorrect free operation in sc_pkcs15_decode_prkdf_entry.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NDSQLMZZYBHO5X3BK7D6E7E6NZIMZDI5/
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=18478
- https://github.com/OpenSC/OpenSC/commit/6ce6152284c47ba9b1d4fe8ff9d2e6a3f5ee02c7
- http://www.openwall.com/lists/oss-security/2019/12/29/1
