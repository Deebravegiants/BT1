# [H] CVE-2022-44638

## Summary
Severity: High
Advisory: CVE-2022-44638
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-11-03
Source: https://osv.dev/vulnerability/CVE-2022-44638
Type: osv

## Details
In libpixman in Pixman before 0.42.2, there is an out-of-bounds write (aka heap-based buffer overflow) in rasterize_edges_8 due to an integer overflow in pixman_sample_floor_y.

## References
- http://packetstormsecurity.com/files/170121/pixman-pixman_sample_floor_y-Integer-Overflow.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/44xxx/CVE-2022-44638.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AJ5VY2VYXE4WTRGQ6LMGLF6FV3SY37YE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BY4OPSIB33ETNUXZY2UPZ4NGQ3OKDY4D/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IUJ2BULJTZ2BMSKQHB6US674P55UCWWS/
- https://nvd.nist.gov/vuln/detail/CVE-2022-44638
- https://www.debian.org/security/2022/dsa-5276
- https://gitlab.freedesktop.org/pixman/pixman/-/issues/63
- http://www.openwall.com/lists/oss-security/2022/11/05/1
- https://lists.debian.org/debian-lts-announce/2022/11/msg00008.html
