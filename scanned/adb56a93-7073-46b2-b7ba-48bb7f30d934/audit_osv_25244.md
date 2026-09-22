# [H] OpenPrinting CUPS vulnerable to heap buffer overflow

## Summary
Severity: High
Advisory: CVE-2023-32324
Aliases: GHSA-cxc6-w2g7-69p7
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-06-01
Source: https://osv.dev/vulnerability/CVE-2023-32324
Type: osv

## Details
OpenPrinting CUPS is an open source printing system. In versions 2.4.2 and prior, a heap buffer overflow vulnerability would allow a remote attacker to launch a denial of service (DoS) attack. A buffer overflow vulnerability in the function `format_log_line` could allow remote attackers to cause a DoS on the affected system. Exploitation of the vulnerability can be triggered when the configuration file `cupsd.conf` sets the value of `loglevel `to `DEBUG`. No known patches or workarounds exist at time of publication.

## References
- https://lists.debian.org/debian-lts-announce/2023/06/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32324.json
- https://github.com/OpenPrinting/cups/security/advisories/GHSA-cxc6-w2g7-69p7
- https://nvd.nist.gov/vuln/detail/CVE-2023-32324
