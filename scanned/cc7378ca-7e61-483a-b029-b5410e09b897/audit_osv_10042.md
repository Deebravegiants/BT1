# [C] CVE-2017-12865

## Summary
Severity: Critical
Advisory: CVE-2017-12865
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-08-29
Source: https://osv.dev/vulnerability/CVE-2017-12865
Type: osv

## Details
Stack-based buffer overflow in "dnsproxy.c" in connman 1.34 and earlier allows remote attackers to cause a denial of service (crash) or execute arbitrary code via a crafted response query string passed to the "name" variable.

## References
- http://www.debian.org/security/2017/dsa-3956
- http://www.securityfocus.com/bid/100498
- https://01.org/security/intel-oss-10001/intel-oss-10001
- https://security.gentoo.org/glsa/201812-02
- https://www.nri-secure.com/blog/new-iot-vulnerability-connmando
- https://bugzilla.redhat.com/show_bug.cgi?id=1483720
- https://git.kernel.org/pub/scm/network/connman/connman.git/commit/?id=5c281d182ecdd0a424b64f7698f32467f8f67b71
