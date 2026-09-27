# [M] CVE-2024-2193

## Summary
Severity: Medium
Advisory: CVE-2024-2193
CVSS: 5.7 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-03-15
Source: https://osv.dev/vulnerability/CVE-2024-2193
Type: osv

## Details
A Speculative Race Condition (SRC) vulnerability that impacts modern CPU architectures supporting speculative execution (related to Spectre V1) has been disclosed. An unauthenticated attacker can exploit this vulnerability to disclose arbitrary data from the CPU using race conditions to access the speculative executable code paths.

## References
- http://www.openwall.com/lists/oss-security/2024/03/12/14
- https://download.vusec.net/papers/ghostrace_sec24.pdf
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZON4TLXG7TG4A2XZG563JMVTGQW4SF3A/
- https://www.amd.com/en/resources/product-security/bulletin/amd-sb-7016.html
- https://www.kb.cert.org/vuls/id/488902
- https://www.vusec.net/projects/ghostrace/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/patch/?id=944d5fe50f3f03daacfea16300e656a1691c4a23
- https://ibm.github.io/system-security-research-updates/2024/03/12/ghostrace
- https://kb.cert.org/vuls/id/488902
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/EIUICU6CVJUIB6BPJ7P5QTPQR5VOBHFK/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/H63LGAQXPEVJOES73U4XK65I6DASOAAG/
- http://xenbits.xen.org/xsa/advisory-453.html
- https://xenbits.xen.org/xsa/advisory-453.html
