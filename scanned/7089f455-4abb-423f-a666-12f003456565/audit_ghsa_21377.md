# [M] OctoRPKI crashes when max iterations is reached

## Summary
Severity: Medium
Advisory: GHSA-pmw9-567p-68pc
CVE: CVE-2022-3616
CWE: CWE-754, CWE-834
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2022-10-31
Source: https://github.com/advisories/GHSA-pmw9-567p-68pc
Type: github-advisory

## Affected
- Go: `github.com/cloudflare/cfrpki` — affected >=0 <1.4.4

## Details
### Impact
Attackers can create long chains of CAs that would lead to OctoRPKI exceeding its max iterations parameter. In consequence it would cause the program to crash, preventing it from finishing the validation and leading to a denial of service. Credits to Donika Mirdita and Haya Shulman - Fraunhofer SIT, ATHENE, who discovered and reported this vulnerability.

### Specific Go Packages Affected
github.com/cloudflare/cfrpki/cmd/octorpki

### Patches
This issue is fixed in v1.4.4

### Workarounds
None.

## References
- https://github.com/cloudflare/cfrpki/security/advisories/GHSA-pmw9-567p-68pc
- https://nvd.nist.gov/vuln/detail/CVE-2022-3616
- https://github.com/cloudflare/cfrpki/commit/5f64bcd13477b29cd7ddff6fff3c65dfac3423ca
- https://github.com/cloudflare/cfrpki
