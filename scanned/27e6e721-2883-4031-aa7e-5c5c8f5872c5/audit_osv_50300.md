# [H] CVE-2020-11741

## Summary
Severity: High
Advisory: CVE-2020-11741
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2020-04-14
Source: https://osv.dev/vulnerability/CVE-2020-11741
Type: osv

## Details
An issue was discovered in xenoprof in Xen through 4.13.x, allowing guest OS users (with active profiling) to obtain sensitive information about other guests, cause a denial of service, or possibly gain privileges. For guests for which "active" profiling was enabled by the administrator, the xenoprof code uses the standard Xen shared ring structure. Unfortunately, this code did not treat the guest as a potential adversary: it trusts the guest not to modify buffer size information or modify head / tail pointers in unexpected ways. This can crash the host (DoS). Privilege escalation cannot be ruled out.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5M2XRNCHOGGTJQBZQJ7DCV6ZNAKN3LE2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NVTP4OYHCTRU3ONFJOFJQVNDFB25KLLG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YMAW7D2MP6RE4BFI5BZWOBBWGY3VSOFN/
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00006.html
- https://security.gentoo.org/glsa/202005-08
- https://www.debian.org/security/2020/dsa-4723
- https://xenbits.xen.org/xsa/advisory-313.html
- http://www.openwall.com/lists/oss-security/2020/04/14/1
- http://xenbits.xen.org/xsa/advisory-313.html
