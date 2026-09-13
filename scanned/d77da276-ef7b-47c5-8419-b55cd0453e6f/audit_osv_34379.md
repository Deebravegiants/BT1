# [H] Suricata's improper use of entropy keyword can lead to a NULL-ptr deref

## Summary
Severity: High
Advisory: CVE-2025-59148
Aliases: GHSA-5qf6-92xg-3rr3
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-59148
Type: osv

## Details
Suricata is a network IDS, IPS and NSM engine developed by the OISF (Open Information Security Foundation) and the Suricata community. Versions 8.0.0 and below incorrectly handle the entropy keyword when not anchored to a "sticky" buffer, which can lead to a segmentation fault. This issue is fixed in version 8.0.1. To workaround this issue, users can disable rules using the entropy keyword, or validate they are anchored to a sticky buffer.

## References
- https://forum.suricata.io/t/suricata-8-0-1-and-7-0-12-released/6018
- https://redmine.openinfosecfoundation.org/issues/7838
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59148.json
- https://github.com/OISF/suricata/security/advisories/GHSA-5qf6-92xg-3rr3
- https://nvd.nist.gov/vuln/detail/CVE-2025-59148
- https://github.com/OISF/suricata/commit/9f32550e18f97ea5d610dd7c36aab0ba142c096c
