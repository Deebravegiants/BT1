# [M] Potential CSV Injection vector in OctoberCMS

## Summary
Severity: Medium
Advisory: GHSA-4rhm-m2fp-hx7q
CVE: CVE-2020-5299
CWE: CWE-77
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-06-03
Source: https://github.com/advisories/GHSA-4rhm-m2fp-hx7q
Type: github-advisory

## Affected
- Packagist: `october/backend` — affected >=1.0.319 <1.0.466

## Details
### Impact
Any users with the ability to modify any data that could eventually be exported as a CSV file from the `ImportExportController` could potentially introduce a CSV injection into the data to cause the generated CSV export file to be malicious. This requires attackers to achieve the following before a successful attack can be completed: 

1. Have found a vulnerability in the victim's spreadsheet software of choice.
2. Control data that would potentially be exported through the `ImportExportController` by a theoretical victim.
3. Convince the victim to export above data as a CSV and run it in vulnerable spreadsheet software while also bypassing any sanity checks by said software.

### Patches
Issue has been patched in Build 466 (v1.0.466).

### Workarounds
Apply https://github.com/octobercms/library/commit/c84bf03f506052c848f2fddc05f24be631427a1a & https://github.com/octobercms/october/commit/802d8c8e09a2b342649393edb6d3ceb958851484 to your installation manually if unable to upgrade to Build 466.

### References
Reported by @chrisvidal initially & [Sivanesh Ashok](https://stazot.com/) later.

### For more information
If you have any questions or comments about this advisory:
* Email us at [hello@octobercms.com](mailto:hello@octobercms.com)

### Threat assessment:
Given the number of hoops that a potential attacker would have to jump through, this vulnerability really boils down to the possibility of abusing the trust that a user may have in the export functionality of the project. Thus, this has been rated low severity as it requires vulnerabilities to also exist in other software used by any potential victims as well as successful social engineering attacks.

## References
- https://github.com/octobercms/october/security/advisories/GHSA-4rhm-m2fp-hx7q
- https://nvd.nist.gov/vuln/detail/CVE-2020-5299
- https://github.com/octobercms/library/commit/c84bf03f506052c848f2fddc05f24be631427a1a
- https://github.com/octobercms/october/commit/802d8c8e09a2b342649393edb6d3ceb958851484
- http://packetstormsecurity.com/files/158730/October-CMS-Build-465-XSS-File-Read-File-Deletion-CSV-Injection.html
- http://seclists.org/fulldisclosure/2020/Aug/2
