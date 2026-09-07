# [M] Reflected XSS when importing CSV in OctoberCMS

## Summary
Severity: Medium
Advisory: GHSA-gg6x-xx78-448c
CVE: CVE-2020-5298
CWE: CWE-79, CWE-87
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-06-03
Source: https://github.com/advisories/GHSA-gg6x-xx78-448c
Type: github-advisory

## Affected
- Packagist: `october/backend` — affected >=1.0.319 <1.0.466

## Details
### Impact
A user with the ability to use the import functionality of the `ImportExportController` behavior could be socially engineered by an attacker to upload a maliciously crafted CSV file which could result in a reflected XSS attack on the user in question

### Patches
Issue has been patched in Build 466 (v1.0.466).

### Workarounds
Apply https://github.com/octobercms/october/commit/cd0b6a791f995d86071a024464c1702efc50f46c to your installation manually if unable to upgrade to Build 466.

### References
Reported by [Sivanesh Ashok](https://stazot.com/)

### For more information
If you have any questions or comments about this advisory:
* Email us at [hello@octobercms.com](mailto:hello@octobercms.com)

### Threat assessment:
<img width="1100" alt="Screen Shot 2020-03-31 at 2 01 52 PM" src="https://user-images.githubusercontent.com/7253840/78070158-8f7ef580-7358-11ea-950c-226533f6a0a3.png">

## References
- https://github.com/octobercms/october/security/advisories/GHSA-gg6x-xx78-448c
- https://nvd.nist.gov/vuln/detail/CVE-2020-5298
- https://github.com/octobercms/october/commit/cd0b6a791f995d86071a024464c1702efc50f46c
- http://packetstormsecurity.com/files/158730/October-CMS-Build-465-XSS-File-Read-File-Deletion-CSV-Injection.html
- http://seclists.org/fulldisclosure/2020/Aug/2
