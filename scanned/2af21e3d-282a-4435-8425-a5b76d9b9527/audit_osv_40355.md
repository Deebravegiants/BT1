# [M] Permissive Cross-domain Policy with Untrusted Domains in coolercontrold

## Summary
Severity: Medium
Advisory: CVE-2026-5302
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-5302
Type: osv

## Details
CORS misconfiguration in CoolerControl/coolercontrold <4.0.0 allows unauthenticated remote attackers to read data and send commands to the service via malicious websites

## References
- https://gitlab.com/coolercontrol/coolercontrol/-/blob/2.0.0/coolercontrold/src/api/mod.rs?ref_type=tags#L374
- https://gitlab.com/coolercontrol/coolercontrol/-/releases/4.0.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5302.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5302
