# [M] Local File read vulnerability in OctoberCMS

## Summary
Severity: Medium
Advisory: GHSA-r23f-c2j5-rx2f
CVE: CVE-2020-5295
CWE: CWE-829, CWE-98
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-06-03
Source: https://github.com/advisories/GHSA-r23f-c2j5-rx2f
Type: github-advisory

## Affected
- Packagist: `october/cms` — affected >=1.0.319 <1.0.466

## Details
### Impact
An attacker can exploit this vulnerability to read local files of an October CMS server. The vulnerability is only exploitable by an authenticated backend user with the `cms.manage_assets` permission.

### Patches
Issue has been patched in Build 466 (v1.0.466).

### Workarounds
Apply https://github.com/octobercms/october/commit/2b8939cc8b5b6fe81e093fe2c9f883ada4e3c8cc to your installation manually if unable to upgrade to Build 466.

### References
Reported by [Sivanesh Ashok](https://stazot.com/)

### For more information
If you have any questions or comments about this advisory:
* Email us at [hello@octobercms.com](mailto:hello@octobercms.com)

### Threat assessment:
<img width="1108" alt="Screen Shot 2020-03-31 at 2 37 53 PM" src="https://user-images.githubusercontent.com/7253840/78072989-44b3ac80-735d-11ea-8676-09c69f0409c4.png">

## References
- https://github.com/octobercms/october/security/advisories/GHSA-r23f-c2j5-rx2f
- https://nvd.nist.gov/vuln/detail/CVE-2020-5295
- https://github.com/octobercms/october/commit/2b8939cc8b5b6fe81e093fe2c9f883ada4e3c8cc
- http://packetstormsecurity.com/files/158730/October-CMS-Build-465-XSS-File-Read-File-Deletion-CSV-Injection.html
- http://seclists.org/fulldisclosure/2020/Aug/2
