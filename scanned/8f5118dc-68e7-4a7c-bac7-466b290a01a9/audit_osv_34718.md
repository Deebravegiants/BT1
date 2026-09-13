# [H] Suricata is vulnerable to unbounded memory growth for decompression

## Summary
Severity: High
Advisory: CVE-2025-64334
Aliases: GHSA-r5jf-v2gx-gx8w
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-26
Source: https://osv.dev/vulnerability/CVE-2025-64334
Type: osv

## Details
Suricata is a network IDS, IPS and NSM engine developed by the OISF (Open Information Security Foundation) and the Suricata community. In versions from 8.0.0 to before 8.0.2, compressed HTTP data can lead to unbounded memory growth during decompression. This issue has been patched in version 8.0.2. A workaround involves disabling LZMA decompression or limiting response-body-limit size.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64334.json
- https://github.com/OISF/suricata/security/advisories/GHSA-r5jf-v2gx-gx8w
- https://nvd.nist.gov/vuln/detail/CVE-2025-64334
- https://github.com/OISF/suricata/commit/00f04daa3a44928dfdd0003cb9735469272c94a1
