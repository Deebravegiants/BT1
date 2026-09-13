# [M] CVE-2020-11740

## Summary
Severity: Medium
Advisory: CVE-2020-11740
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-04-14
Source: https://osv.dev/vulnerability/CVE-2020-11740
Type: osv

## Details
An issue was discovered in xenoprof in Xen through 4.13.x, allowing guest OS users (without active profiling) to obtain sensitive information about other guests. Unprivileged guests can request to map xenoprof buffers, even if profiling has not been enabled for those guests. These buffers were not scrubbed.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5M2XRNCHOGGTJQBZQJ7DCV6ZNAKN3LE2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NVTP4OYHCTRU3ONFJOFJQVNDFB25KLLG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YMAW7D2MP6RE4BFI5BZWOBBWGY3VSOFN/
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00006.html
- https://www.debian.org/security/2020/dsa-4723
- https://security.gentoo.org/glsa/202005-08
- https://xenbits.xen.org/xsa/advisory-313.html
- http://www.openwall.com/lists/oss-security/2020/04/14/1
- http://xenbits.xen.org/xsa/advisory-313.html
