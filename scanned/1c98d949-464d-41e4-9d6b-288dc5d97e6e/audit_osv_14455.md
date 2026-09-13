# [M] CVE-2019-1000019

## Summary
Severity: Medium
Advisory: CVE-2019-1000019
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-02-04
Source: https://osv.dev/vulnerability/CVE-2019-1000019
Type: osv

## Details
libarchive version commit bf9aec176c6748f0ee7a678c5f9f9555b9a757c1 onwards (release v3.0.2 onwards) contains a CWE-125: Out-of-bounds Read vulnerability in 7zip decompression, archive_read_support_format_7zip.c, header_bytes() that can result in a crash (denial of service). This attack appears to be exploitable via the victim opening a specially crafted 7zip file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00015.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CBOCC2M6YGPZA6US43YK4INPSJZZHRTG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZVXA7PHINVT6DFF6PRLTDTVTXKDLVHNF/
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00055.html
- https://access.redhat.com/errata/RHSA-2019:2298
- https://access.redhat.com/errata/RHSA-2019:3698
- https://github.com/libarchive/libarchive/pull/1120
- https://lists.debian.org/debian-lts-announce/2019/02/msg00013.html
- https://usn.ubuntu.com/3884-1/
- https://github.com/libarchive/libarchive/pull/1120/commits/65a23f5dbee4497064e9bb467f81138a62b0dae1
