# [H] Suricata is vulnerable to a stack overflow on larger compressed data

## Summary
Severity: High
Advisory: CVE-2025-64332
Aliases: GHSA-p32q-7wcp-gv92
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-26
Source: https://osv.dev/vulnerability/CVE-2025-64332
Type: osv

## Details
Suricata is a network IDS, IPS and NSM engine developed by the OISF (Open Information Security Foundation) and the Suricata community. Prior to versions 7.0.13 and 8.0.2, a stack overflow that causes Suricata to crash can occur if SWF decompression is enabled. This issue has been patched in versions 7.0.13 and 8.0.2. A workaround for this issue involves disabling SWF decompression (swf-decompression in suricata.yaml), it is disabled by default; set decompress-depth to lower than half your stack size if swf-decompression must be enabled.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64332.json
- https://github.com/OISF/suricata/security/advisories/GHSA-p32q-7wcp-gv92
- https://nvd.nist.gov/vuln/detail/CVE-2025-64332
- https://github.com/OISF/suricata/commit/ad446c9006a77490af51c468aae0ce934f4d2117
