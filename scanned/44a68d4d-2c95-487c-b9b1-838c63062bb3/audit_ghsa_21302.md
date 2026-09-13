# [H] October CMS Safe Mode bypass leads to authenticated Remote Code Execution

## Summary
Severity: High
Advisory: GHSA-x4q7-m6fp-4v9v
CVE: CVE-2022-35944
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-13
Source: https://github.com/advisories/GHSA-x4q7-m6fp-4v9v
Type: github-advisory

## Affected
- Packagist: `october/system` — affected >=2.0.0 <2.2.34
- Packagist: `october/system` — affected >=3.0.0 <3.0.66

## Details
### Impact

This vulnerability only affects installations that rely on the safe mode restriction, commonly used when providing public access to the admin panel. Assuming an attacker has access to the admin panel and permission to open the "Editor" section, they can bypass the Safe Mode (`cms.safe_mode`) restriction to introduce new PHP code in a CMS template using a specially crafted request.

### Patches

The issue has been patched in v2.2.34 and v3.0.66

### References

Credits to:

-  David Miller

### For more information

If you have any questions or comments about this advisory:

- Email us at [hello@octobercms.com](mailto:hello@octobercms.com)

## References
- https://github.com/octobercms/october/security/advisories/GHSA-x4q7-m6fp-4v9v
- https://nvd.nist.gov/vuln/detail/CVE-2022-35944
- https://github.com/octobercms/october
