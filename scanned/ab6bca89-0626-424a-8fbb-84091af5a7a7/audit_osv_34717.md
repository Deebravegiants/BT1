# [H] Suricata is vulnerable to a stack overflow from big content-type

## Summary
Severity: High
Advisory: CVE-2025-64333
Aliases: GHSA-537h-xxmx-v87m
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-26
Source: https://osv.dev/vulnerability/CVE-2025-64333
Type: osv

## Details
Suricata is a network IDS, IPS and NSM engine developed by the OISF (Open Information Security Foundation) and the Suricata community. Prior to versions 7.0.13 and 8.0.2, a large HTTP content type, when logged can cause a stack overflow crashing Suricata. This issue has been patched in versions 7.0.13 and 8.0.2. A workaround for this issue involves limiting stream.reassembly.depth to less then half the stack size. Increasing the process stack size makes it less likely the bug will trigger.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64333.json
- https://github.com/OISF/suricata/security/advisories/GHSA-537h-xxmx-v87m
- https://nvd.nist.gov/vuln/detail/CVE-2025-64333
