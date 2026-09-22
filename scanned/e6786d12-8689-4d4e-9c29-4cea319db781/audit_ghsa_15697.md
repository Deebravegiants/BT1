# [M] PheonixAppAPI has visible Encoding Maps

## Summary
Severity: Medium
Advisory: GHSA-258h-f687-4226
CVE: CVE-2024-41951
CWE: CWE-323
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-07-31
Source: https://github.com/advisories/GHSA-258h-f687-4226
Type: github-advisory

## Affected
- PyPI: `PheonixAppAPI` — affected >=0 <0.2.5

## Details
### Impact
This is a kind of moderate issue. The impact is not big for normal users but can be for users who want to secure their code/files/etc.

The issue is that the map of encoding/decoding languages are visible in code. 

### Patches
The Problem was patched in 0.2.5, so you should try to upgrade to the 0.2.5 version.

### For 0.2.5 version users
Please run the post_install.py file inside the Scripts folder after downloading from pip.

### Workarounds
There is a fix to this problem but it requires modifying the code. Modifying the code can lead to more issues.

### References
There are currently no references to this problem.

### NOTE: If you get a error regarding a function like -> get_key() or something like that, please re-run the file post_install.py inside Scripts folder

## References
- https://github.com/AkshuDev/PheonixAppAPI/security/advisories/GHSA-258h-f687-4226
- https://nvd.nist.gov/vuln/detail/CVE-2024-41951
- https://github.com/AkshuDev/PheonixAppAPI/commit/0937419e323f5ea9013d43dc1b82fef9d7e05044
- https://github.com/AkshuDev/PheonixAppAPI
