# [C] pyminizip affected by zlib's integer overflow/heap based buffer overflow vulnerability due to vulnerable dependency

## Summary
Severity: Critical
Advisory: GHSA-mq29-j5xf-cjwr
CVE: CVE-2023-45853
CWE: CWE-190
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-14
Source: https://github.com/advisories/GHSA-mq29-j5xf-cjwr
Type: github-advisory

## Affected
- PyPI: `pyminizip` — affected >=0

## Details
MiniZip in zlib through 1.3 has an integer overflow and resultant heap-based buffer overflow in zipOpenNewFileInZip4_64 via a long filename, comment, or extra field. NOTE: MiniZip is not a supported part of the zlib product.

pyminizip uses version 1.2.11 of zlib's code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-45853
- https://github.com/madler/zlib/pull/843
- https://github.com/madler/zlib/commit/73331a6a0481067628f065ffe87bb1d8f787d10c
- https://chromium.googlesource.com/chromium/src/+/d709fb23806858847131027da95ef4c548813356
- https://chromium.googlesource.com/chromium/src/+/de29dd6c7151d3cd37cb4cf0036800ddfb1d8b61
- https://github.com/madler/zlib/blob/ac8f12c97d1afd9bafa9c710f827d40a407d3266/contrib/README.contrib#L1-L4
- https://github.com/smihica/pyminizip
- https://github.com/smihica/pyminizip/blob/master/zlib-1.2.11/contrib/minizip/zip.c
- https://lists.debian.org/debian-lts-announce/2023/11/msg00026.html
- https://pypi.org/project/pyminizip/#history
- https://security.gentoo.org/glsa/202401-18
- https://security.netapp.com/advisory/ntap-20231130-0009
- https://www.winimage.com/zLibDll/minizip.html
- http://www.openwall.com/lists/oss-security/2023/10/20/9
- http://www.openwall.com/lists/oss-security/2024/01/24/10
