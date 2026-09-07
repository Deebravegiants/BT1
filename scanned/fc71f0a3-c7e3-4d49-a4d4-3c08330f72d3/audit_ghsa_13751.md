# [M] October CMS stored XSS by authenticated backend user with improper configuration

## Summary
Severity: Medium
Advisory: GHSA-rvx8-p3xp-fj3p
CVE: CVE-2023-44383
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-11-29
Source: https://github.com/advisories/GHSA-rvx8-p3xp-fj3p
Type: github-advisory

## Affected
- Packagist: `october/system` — affected >=3.0.0 <3.5.2

## Details
### Impact

A user with access to the media manager that stores SVG files could create a stored XSS attack against themselves and any other user with access to the media manager when SVG files are supported.

SVG files are supported by default in v3 for convenience; however, this has resulted in multiple mistaken vulnerability reports from security researchers. As per the documentation, if a backend user is not trusted, the advice is to remove the `svg` extension from the list of supported file types.

### Patches

The issue has been patched in v3.5.2 by including an SVG sanister. It is enabled by default for new installations but must be enabled for existing sites in the **config/media.php** file.

```
'clean_vectors' => true,
```

### Workarounds

If you cannot upgrade for this patch, follow the pervious advice and remove `svg` from the supported file types.

### References

- https://github.com/octobercms/october/blob/3.x/config/media.php

Credits to:
- Faris Krivic
- Okan Kurtulus
- Aldin Visnjic
- Bug Shankar

### For more information
If you have any questions or comments about this advisory:
* Email us at [hello@octobercms.com](mailto:hello@octobercms.com)

## References
- https://github.com/octobercms/october/security/advisories/GHSA-rvx8-p3xp-fj3p
- https://nvd.nist.gov/vuln/detail/CVE-2023-44383
- https://github.com/octobercms/october/commit/b7eed0bbf54d07ff310fcdc7037a8e8bf1f5043b
- https://github.com/octobercms/october
