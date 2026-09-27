# [H] wire-avs remote format string vulnerability

## Summary
Severity: High
Advisory: CVE-2023-48221
Aliases: GHSA-m4xg-fcr3-w3pq
CVSS: 7.3 (CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:C/C:N/I:H/A:H)
Published: 2023-11-20
Source: https://osv.dev/vulnerability/CVE-2023-48221
Type: osv

## Details
wire-avs provides Audio, Visual, and Signaling (AVS) functionality sure the secure messaging software Wire. Prior to versions 9.2.22 and 9.3.5, a remote format string vulnerability could potentially allow an attacker to cause a denial of service or possibly execute arbitrary code. The issue has been fixed in wire-avs 9.2.22 & 9.3.5 and is already included on all Wire products. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/48xxx/CVE-2023-48221.json
- https://github.com/wireapp/wire-avs/security/advisories/GHSA-m4xg-fcr3-w3pq
- https://nvd.nist.gov/vuln/detail/CVE-2023-48221
- https://github.com/wireapp/wire-avs/commit/364c3326a1331a84607bce2e17126306d39150cd
