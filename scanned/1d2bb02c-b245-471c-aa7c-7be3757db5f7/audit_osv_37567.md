# [H] Suricata dcerpc: quadratic complexity in dcerpc buffering

## Summary
Severity: High
Advisory: CVE-2026-31937
Aliases: GHSA-86vg-w8vm-m3gg
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-31937
Type: osv

## Details
Suricata is a network IDS, IPS and NSM engine. Prior to version 7.0.15, inefficiency in DCERPC buffering can lead to a performance degradation. This issue has been patched in version 7.0.15.

## References
- https://redmine.openinfosecfoundation.org/issues/8304
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31937.json
- https://github.com/OISF/suricata/security/advisories/GHSA-86vg-w8vm-m3gg
- https://nvd.nist.gov/vuln/detail/CVE-2026-31937
