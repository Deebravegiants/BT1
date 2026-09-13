# [H] Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection') in coolercontrold

## Summary
Severity: High
Advisory: CVE-2026-5208
CVSS: 8.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-5208
Type: osv

## Details
Command injection in alerts in CoolerControl/coolercontrold <4.0.0 allows authenticated attackers to execute arbitrary code as root via injected bash commands in alert names

## References
- https://gitlab.com/coolercontrol/coolercontrol/-/blob/3.1.0/coolercontrold/src/alerts.rs?ref_type=tags#L576
- https://gitlab.com/coolercontrol/coolercontrol/-/releases/4.0.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5208.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5208
