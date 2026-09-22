# [C] xrdp: Heap buffer overflow in NeutrinoRDP channel reassembly

## Summary
Severity: Critical
Advisory: CVE-2026-32623
Aliases: GHSA-phw3-qp59-x2v4
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-32623
Type: osv

## Details
xrdp is an open source RDP server. Versions through 0.10.5 contain a heap-based buffer overflow vulnerability in the NeutrinoRDP module. When proxying RDP sessions from xrdp to another server, the module fails to properly validate the size of reassembled fragmented virtual channel data against its allocated memory buffer. A malicious downstream RDP server (or an attacker capable of performing a Man-in-the-Middle attack) could exploit this flaw to cause memory corruption, potentially leading to a Denial of Service (DoS) or Remote Code Execution (RCE). The NeutrinoRDP module is not built by default. This vulnerability only affects environments where the module has been explicitly compiled and enabled. Users can verify if the module is built by checking for --enable-neutrinordp in the output of the xrdp -v command. This issue has been fixed in version 0.10.6.

## References
- https://github.com/neutrinolabs/xrdp/releases/tag/v0.10.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32623.json
- https://github.com/neutrinolabs/xrdp/security/advisories/GHSA-phw3-qp59-x2v4
- https://nvd.nist.gov/vuln/detail/CVE-2026-32623
