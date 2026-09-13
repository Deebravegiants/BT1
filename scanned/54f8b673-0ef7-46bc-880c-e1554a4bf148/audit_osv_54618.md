# [M] CVE-2024-2201

## Summary
Severity: Medium
Advisory: CVE-2024-2201
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-12-19
Source: https://osv.dev/vulnerability/CVE-2024-2201
Type: osv

## Details
A cross-privilege Spectre v2 vulnerability allows attackers to bypass all deployed mitigations, including the recent Fine(IBT), and to leak arbitrary Linux kernel memory on Intel systems.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/D5OK6MH75S7YWD34EWW7QIZTS627RIE3/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RYAZ7P6YFJ2E3FHKAGIKHWS46KYMMTZH/
- https://www.kb.cert.org/vuls/id/155143
- http://www.openwall.com/lists/oss-security/2024/05/07/7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6QKNCPX7CJUK4I6BRGABAUQK2DMQZUCA/
- http://www.openwall.com/lists/oss-security/2024/04/09/15
- http://xenbits.xen.org/xsa/advisory-456.html
- https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/advisory-guidance/branch-history-injection.htm
- https://github.com/vusec/inspectre-gadget?tab=readme-ov-file
