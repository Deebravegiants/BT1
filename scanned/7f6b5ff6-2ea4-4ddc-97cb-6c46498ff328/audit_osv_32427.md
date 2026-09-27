# [M] Suricata pcre: negated pcr can cause infinite loop

## Summary
Severity: Medium
Advisory: CVE-2025-29918
Aliases: GHSA-924c-vvm5-9mqx
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-10
Source: https://osv.dev/vulnerability/CVE-2025-29918
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine. A PCRE rule can be written that leads to an infinite loop when negated PCRE is used. Packet processing thread becomes stuck in infinite loop limiting visibility and availability in inline mode. This vulnerability is fixed in 7.0.9.

## References
- https://lists.debian.org/debian-lts-announce/2025/03/msg00029.html
- https://redmine.openinfosecfoundation.org/issues/7526
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/29xxx/CVE-2025-29918.json
- https://github.com/OISF/suricata/security/advisories/GHSA-924c-vvm5-9mqx
- https://nvd.nist.gov/vuln/detail/CVE-2025-29918
- https://github.com/OISF/suricata/commit/b14c67cbdf25fa6c7ffe0d04ddf3ebe67b12b50b
