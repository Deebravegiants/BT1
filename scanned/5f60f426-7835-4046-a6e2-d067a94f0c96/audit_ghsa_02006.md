# [C] elFinder before 2.1.59 contains multiple vulnerabilities leading to RCE

## Summary
Severity: Critical
Advisory: GHSA-wph3-44rj-92pr
CVE: CVE-2021-32682
CWE: CWE-22, CWE-78, CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-16
Source: https://github.com/advisories/GHSA-wph3-44rj-92pr
Type: github-advisory

## Affected
- Packagist: `studio-42/elfinder` — affected >=0 <2.1.59

## Details
### Impact

We recently fixed several vulnerabilities affect elFinder 2.1.58. These vulnerabilities can allow an attacker to execute arbitrary code and commands on the server hosting the elFinder PHP connector, even with the minimal configuration. 

### Patches

The issues were addressed in our last release, 2.1.59. 

### Workarounds

If you can't update to 2.1.59, make sure your connector is not exposed without authentication.

### Reference

Further technical details will be disclosed on https://blog.sonarsource.com/tag/security after some time.

### For more information

If you have any questions or comments about this advisory, you can contact:
    - The original reporters, by sending an email to vulnerability.research@sonarsource.com;
    - The maintainers, by opening an issue on this repository.

## References
- https://github.com/Studio-42/elFinder/security/advisories/GHSA-qm58-cvvm-c5qr
- https://github.com/Studio-42/elFinder/security/advisories/GHSA-wph3-44rj-92pr
- https://nvd.nist.gov/vuln/detail/CVE-2021-32682
- https://github.com/Studio-42/elFinder/commit/a106c350b7dfe666a81d6b576816db9fe0899b17
- https://blog.sonarsource.com/elfinder-case-study-of-web-file-manager-vulnerabilities
- https://github.com/Studio-42/elFinder
- http://packetstormsecurity.com/files/164173/elFinder-Archive-Command-Injection.html
