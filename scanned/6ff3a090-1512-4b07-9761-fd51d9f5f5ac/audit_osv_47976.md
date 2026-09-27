# [H] CVE-2017-16227

## Summary
Severity: High
Advisory: CVE-2017-16227
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-29
Source: https://osv.dev/vulnerability/CVE-2017-16227
Type: osv

## Details
The aspath_put function in bgpd/bgp_aspath.c in Quagga before 1.2.2 allows remote attackers to cause a denial of service (session drop) via BGP UPDATE messages, because AS_PATH size calculation for long paths counts certain bytes twice and consequently constructs an invalid message.

## References
- http://download.savannah.gnu.org/releases/quagga/quagga-1.2.2.changelog.txt
- http://www.debian.org/security/2017/dsa-4011
- https://bugs.debian.org/879474
- https://git.savannah.gnu.org/cgit/quagga.git/commit/?id=7a42b78be9a4108d98833069a88e6fddb9285008
- https://lists.quagga.net/pipermail/quagga-dev/2017-September/033284.html
