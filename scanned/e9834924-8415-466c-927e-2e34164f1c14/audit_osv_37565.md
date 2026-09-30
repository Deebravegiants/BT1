# [H] Suricata http2: unbounded resource consumption

## Summary
Severity: High
Advisory: CVE-2026-31935
Aliases: GHSA-vxrp-5pg7-7v4x
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-31935
Type: osv

## Details
Suricata is a network IDS, IPS and NSM engine. Prior to versions 7.0.15 and 8.0.4, flooding of craft HTTP2 continuation frames can lead to memory exhaustion, usually resulting in the Suricata process being shut down by the operating system. This issue has been patched in versions 7.0.15 and 8.0.4.

## References
- https://redmine.openinfosecfoundation.org/issues/8289
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31935.json
- https://github.com/OISF/suricata/security/advisories/GHSA-vxrp-5pg7-7v4x
- https://nvd.nist.gov/vuln/detail/CVE-2026-31935
