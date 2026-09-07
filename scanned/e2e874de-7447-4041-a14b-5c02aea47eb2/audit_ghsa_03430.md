# [M] JavaScript execution via malicious molfiles (XSS)

## Summary
Severity: Medium
Advisory: GHSA-2pwh-52h7-7j84
CVE: CVE-2024-0758
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-04-16
Source: https://github.com/advisories/GHSA-2pwh-52h7-7j84
Type: github-advisory

## Affected
- Maven: `de.ipb-halle:molecularfaces` — affected >=0 <0.3.0

## Details
### Impact
The viewer plugin implementation of `<mol:molecule>` renders molfile data directly inside a `<script>` tag without any escaping. Arbitrary JavaScript code can thus be executed in the client browser via crafted molfiles.

### Patches
Patched in v0.3.0: Molfile data is now rendered as value of a hidden `<input>` tag and escaped via JSF's mechanisms.

### Workarounds
No workaround available.

## References
- https://github.com/ipb-halle/MolecularFaces/security/advisories/GHSA-2pwh-52h7-7j84
- https://nvd.nist.gov/vuln/detail/CVE-2024-0758
- https://github.com/ipb-halle/MolecularFaces
- https://vulncheck.com/advisories/vc-advisory-GHSA-2pwh-52h7-7j84
