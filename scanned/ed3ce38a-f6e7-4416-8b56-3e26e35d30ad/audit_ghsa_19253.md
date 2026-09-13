# [C] OpenPubkey Vulnerable to Authentication Bypass

## Summary
Severity: Critical
Advisory: GHSA-537f-gxgm-3jjq
CVE: CVE-2025-3757
CWE: CWE-305
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:L/SC:L/SI:L/SA:L (CVSS_V4)
Published: 2025-05-13
Source: https://github.com/advisories/GHSA-537f-gxgm-3jjq
Type: github-advisory

## Affected
- Go: `github.com/openpubkey/openpubkey` — affected >=0 <0.10.0

## Details
### Impact

Versions of OpenPubkey library prior to 0.10.0 contained a vulnerability that would allow a specially crafted JWS to bypass signature verification.

### Patches

Upgrade to v0.10.0 or greater. This vulnerability is not present in versions of OpenPubkey after v0.9.0. 

### References

[CVE-2025-3757 ](https://www.cve.org/CVERecord?id=CVE-2025-3757)

## References
- https://github.com/openpubkey/openpubkey/security/advisories/GHSA-537f-gxgm-3jjq
- https://nvd.nist.gov/vuln/detail/CVE-2025-3757
- https://github.com/openpubkey/openpubkey
