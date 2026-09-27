# [M] cups: Remote DoS via null dereference

## Summary
Severity: Medium
Advisory: CVE-2025-58364
Aliases: GHSA-7qx3-r744-6qv4
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-11
Source: https://osv.dev/vulnerability/CVE-2025-58364
Type: osv

## Details
OpenPrinting CUPS is an open source printing system for Linux and other Unix-like operating systems. In versions 2.4.12 and earlier, an unsafe deserialization and validation of printer attributes causes null dereference in the libcups library. This is a remote DoS vulnerability available in local subnet in default configurations. It can cause the cups & cups-browsed to crash, on all the machines in local network who are listening for printers (so by default for all regular linux machines). On systems where the vulnerability CVE-2024-47176 (cups-filters 1.x/cups-browsed 2.x vulnerability) was not fixed, and the firewall on the machine does not reject incoming communication to IPP port, and the machine is set to be available to public internet, attack vector "Network" is possible. The current versions of CUPS and cups-browsed projects have the attack vector "Adjacent" in their default configurations. Version 2.4.13 contains a patch for CVE-2025-58364.

## References
- http://www.openwall.com/lists/oss-security/2025/09/11/2
- https://lists.debian.org/debian-lts-announce/2025/09/msg00013.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58364.json
- https://github.com/OpenPrinting/cups/security/advisories/GHSA-7qx3-r744-6qv4
- https://nvd.nist.gov/vuln/detail/CVE-2025-58364
- https://github.com/OpenPrinting/cups/commit/e58cba9d6fceed4242980e51dbd1302cf638ab1d
