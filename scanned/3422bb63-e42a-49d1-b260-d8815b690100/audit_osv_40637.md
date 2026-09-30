# [C] GetSimple CMS & GetSimpleCMS-CE have an Unauthenticated Admin Account Creation via Setup Logic Flaw

## Summary
Severity: Critical
Advisory: CVE-2026-53952
Aliases: GHSA-rw2c-w4mg-46g4
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-09-11
Source: https://osv.dev/vulnerability/CVE-2026-53952
Type: osv

## Details
GetSimple CMS is a content management system (CMS), and GetSimple CMS CE is the community edition of that CMS. A logic flaw in GetSimple CMS (v3.4.0a and below) and GetSimpleCMS-CE (v3.3.22 and below) allows unauthenticated attackers to create a new administrator account. The application features an automated security control designed to delete the sensitive `admin/setup.php` file post-installation. However, this control is neutralized by a self-exclusion bug within the deletion logic, leaving the setup script accessible for unauthorized account creation even after a legitimate installation is completed. As of time of publication, no known patched versions are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53952.json
- https://github.com/GetSimpleCMS-CE/GetSimpleCMS-CE/security/advisories/GHSA-rw2c-w4mg-46g4
- https://nvd.nist.gov/vuln/detail/CVE-2026-53952
