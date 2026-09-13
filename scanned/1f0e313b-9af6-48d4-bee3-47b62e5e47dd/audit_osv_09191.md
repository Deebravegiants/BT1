# [C] CVE-2016-8863

## Summary
Severity: Critical
Advisory: CVE-2016-8863
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-07
Source: https://osv.dev/vulnerability/CVE-2016-8863
Type: osv

## Details
Heap-based buffer overflow in the create_url_list function in gena/gena_device.c in Portable UPnP SDK (aka libupnp) before 1.6.21 allows remote attackers to cause a denial of service (crash) or possibly execute arbitrary code via a valid URI followed by an invalid one in the CALLBACK header of an SUBSCRIBE request.

## References
- http://www.securityfocus.com/bid/92849
- https://www.tenable.com/security/research/tra-2017-10
- https://security.gentoo.org/glsa/201701-52
- https://sourceforge.net/p/pupnp/code/ci/master/tree/ChangeLog
- https://www.debian.org/security/2016/dsa-3736
- https://sourceforge.net/p/pupnp/bugs/133/
