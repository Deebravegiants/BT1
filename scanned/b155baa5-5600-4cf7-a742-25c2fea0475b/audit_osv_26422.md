# [H] net: dsa: Removed unneeded of_node_put in felix_parse_ports_node

## Summary
Severity: High
Advisory: CVE-2023-53170
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53170
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.4.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: dsa: Removed unneeded of_node_put in felix_parse_ports_node

Remove unnecessary of_node_put from the continue path to prevent
child node from being released twice, which could avoid resource
leak or other unexpected issues.

## References
- https://git.kernel.org/stable/c/04499f28b40bfc24f20b0e2331008bb90a54a6cf
- https://git.kernel.org/stable/c/7ead10b44b79ce8bfcd51e749d54e009de5f511a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53170.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53170
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
