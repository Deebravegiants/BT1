# [M] OctoPrint Unverified Password Change via Access Control Settings

## Summary
Severity: Medium
Advisory: GHSA-5626-pw9c-hmjr
CVE: CVE-2024-23637
CWE: CWE-287, CWE-620
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-01-31
Source: https://github.com/advisories/GHSA-5626-pw9c-hmjr
Type: github-advisory

## Affected
- PyPI: `OctoPrint` — affected >=0 <1.10.0rc1

## Details
### Impact

OctoPrint versions up until and including 1.9.3 contain a vulnerability that allows malicious admins to change the password of other admin accounts, including their own, without having to repeat their password.

An attacker who managed to hijack an admin account might use this to lock out actual admins from their OctoPrint instance.

### Patches

The vulnerability will be patched in version 1.10.0.

### Workarounds

OctoPrint administrators are strongly advised to thoroughly vet who has admin access to their installation.

### Credits

This vulnerability was discovered and responsibly disclosed to OctoPrint by Timothy "TK" Ruppert.

## References
- https://github.com/OctoPrint/OctoPrint/security/advisories/GHSA-5626-pw9c-hmjr
- https://nvd.nist.gov/vuln/detail/CVE-2024-23637
- https://github.com/OctoPrint/OctoPrint/commit/1729d167b4ae4a5835bbc7211b92c6828b1c4125
- https://github.com/OctoPrint/OctoPrint
- https://github.com/OctoPrint/OctoPrint/releases/tag/1.10.0rc1
- https://github.com/pypa/advisory-database/tree/main/vulns/octoprint/PYSEC-2024-29.yaml
