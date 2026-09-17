# [H] Use of Externally-Controlled Format String in wire-avs

## Summary
Severity: High
Advisory: GHSA-2j6v-xpf3-xvrv
CVE: CVE-2021-41193
CWE: CWE-134
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-01
Source: https://github.com/advisories/GHSA-2j6v-xpf3-xvrv
Type: github-advisory

## Affected
- Maven: `com.wire:avs` — affected >=0 <7.1.12

## Details
### Impact
A remote format string vulnerability allowed an attacker to cause a denial of service or possibly execute arbitrary code.

### Patches
* The issue has been fixed in wire-avs 7.1.12 and is already included on all Wire products (currently used version is 8.0.x)

### Workarounds
* No workaround known

### References
* Fixed in commit https://github.com/wireapp/wire-avs/commit/40d373ede795443ae6f2f756e9fb1f4f4ae90bbe

### For more information

If you have any questions or comments about this advisory feel free to email us at [vulnerability-report@wire.com](mailto:vulnerability-report@wire.com)

## References
- https://github.com/wireapp/wire-avs/security/advisories/GHSA-2j6v-xpf3-xvrv
- https://nvd.nist.gov/vuln/detail/CVE-2021-41193
- https://github.com/wireapp/wire-avs/commit/40d373ede795443ae6f2f756e9fb1f4f4ae90bbe
- https://github.com/wireapp/wire-avs
