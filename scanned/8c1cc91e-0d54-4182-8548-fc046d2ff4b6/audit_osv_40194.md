# [H] CVE-2026-50741

## Summary
Severity: High
Advisory: CVE-2026-50741
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-50741
Type: osv

## Details
Bypass to the fix for CVE-2026-34916. Variants of such vectors have been also reported by phucrio and offsetmd. The fix can be bypassed either by sending a disallowed but otherwise valid plugin identifier as `type`, or using the `ox.setChannelTargeting` XML-RPC API method.

## References
- https://hackerone.com/reports/3780854
- https://hackerone.com/reports/3781492
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50741.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-50741
