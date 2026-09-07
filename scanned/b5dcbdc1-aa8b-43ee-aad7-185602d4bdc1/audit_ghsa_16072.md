# [M] Devolutions.XTS.NET Vulnerable to Timing Attack on GF Multiplications

## Summary
Severity: Medium
Advisory: GHSA-j6vm-4r7g-x4gr
CVE: CVE-2024-11862
CWE: CWE-385
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2024-11-27
Source: https://github.com/advisories/GHSA-j6vm-4r7g-x4gr
Type: github-advisory

## Affected
- NuGet: `Devolutions.XTS.NET` — affected >=0 <2024.11.26

## Details
### Impact
Timing attacks on Galois Field multiplications in this package. Successful exploitation would effectively allow a downgrade of the security guarantees of the XTS mode to the security guarantees of ECB mode, allowing block swapping, enabling identification of identical blocks, and rendering half of the XTS key obsolete. Timing attacks require specific conditions to be exploitable.

### Patches
Patched in 2024.11.26

### Workarounds
Upgrade the package

### References
https://en.wikipedia.org/wiki/Timing_attack

## References
- https://github.com/Devolutions/XTS.NET/security/advisories/GHSA-j6vm-4r7g-x4gr
- https://nvd.nist.gov/vuln/detail/CVE-2024-11862
- https://github.com/Devolutions/XTS.NET/commit/fb349d5bfb587218e8603b38ea37f03f036b57fd
- https://github.com/Devolutions/XTS.NET
