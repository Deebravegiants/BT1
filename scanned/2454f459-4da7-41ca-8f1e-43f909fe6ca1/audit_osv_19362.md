# [H] CVE-2021-20304

## Summary
Severity: High
Advisory: CVE-2021-20304
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-08-23
Source: https://osv.dev/vulnerability/CVE-2021-20304
Type: osv

## Details
A flaw was found in OpenEXR's hufDecode functionality. This flaw allows an attacker who can pass a crafted file to be processed by OpenEXR, to trigger an undefined right shift error. The highest threat from this vulnerability is to system availability.

## References
- https://access.redhat.com/security/cve/CVE-2021-20304
- https://security.gentoo.org/glsa/202210-31
- https://bugzilla.redhat.com/show_bug.cgi?id=1939157
- https://github.com/AcademySoftwareFoundation/openexr/commit/51a92d67f53c08230734e74564c807043cbfe41e
- https://github.com/AcademySoftwareFoundation/openexr/pull/849
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=26229
