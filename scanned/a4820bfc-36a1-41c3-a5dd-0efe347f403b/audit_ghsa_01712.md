# [M] Internal NCryptDecrypt method could be used externally from WindowsHello library.

## Summary
Severity: Medium
Advisory: GHSA-wvpv-ffcv-r6cw
CVE: CVE-2020-11005
CWE: CWE-288
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-04-14
Source: https://github.com/advisories/GHSA-wvpv-ffcv-r6cw
Type: github-advisory

## Affected
- NuGet: `HaemmerElectronics.SeppPenner.WindowsHello` — affected >=0 <1.0.4

## Details
### Impact
Every user of the library before version 1.0.4.

### Patches
Patched in 1.0.4+.

### Workarounds
None.

### References
https://github.com/SeppPenner/WindowsHello/issues/3

### For more information
It this library is used to encrypt text and write the output to a txt file, another executable could be able to decrypt the text using the static method NCryptDecrypt from this same library  without the need to use Windows Hello Authentication again.

## References
- https://github.com/SeppPenner/WindowsHello/security/advisories/GHSA-wvpv-ffcv-r6cw
- https://nvd.nist.gov/vuln/detail/CVE-2020-11005
- https://github.com/SeppPenner/WindowsHello/issues/3
