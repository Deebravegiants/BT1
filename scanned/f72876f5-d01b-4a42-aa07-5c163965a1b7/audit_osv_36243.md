# [M] Suricata http1: quadratic complexity in headers parsing over multiple packets

## Summary
Severity: Medium
Advisory: CVE-2026-22263
Aliases: GHSA-rwc5-hxj6-hwx7
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/CVE-2026-22263
Type: osv

## Details
Suricata is a network IDS, IPS and NSM engine. Starting in version 8.0.0 and prior to version 8.0.3, inefficiency in http1 headers parsing can lead to slowdown over multiple packets. Version 8.0.3 patches the issue. No known workarounds are available.

## References
- https://redmine.openinfosecfoundation.org/issues/8201
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22263.json
- https://github.com/OISF/suricata/security/advisories/GHSA-rwc5-hxj6-hwx7
- https://nvd.nist.gov/vuln/detail/CVE-2026-22263
- https://github.com/OISF/suricata/commit/018a377f74e3eb2b042c6f783ad9043060923428
