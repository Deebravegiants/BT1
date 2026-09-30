# [H] CVE-2017-16927

## Summary
Severity: High
Advisory: CVE-2017-16927
CVSS: 8.4 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-23
Source: https://osv.dev/vulnerability/CVE-2017-16927
Type: osv

## Details
The scp_v0s_accept function in sesman/libscp/libscp_v0.c in the session manager in xrdp through 0.9.4 uses an untrusted integer as a write length, which allows local users to cause a denial of service (buffer overflow and application crash) or possibly have unspecified other impact via a crafted input stream.

## References
- https://groups.google.com/forum/#%21topic/xrdp-devel/PmVfMuy_xBA
- https://lists.debian.org/debian-lts-announce/2017/12/msg00005.html
- https://github.com/neutrinolabs/xrdp/pull/958
