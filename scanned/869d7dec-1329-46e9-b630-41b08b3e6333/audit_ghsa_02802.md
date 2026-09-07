# [M] Authenticated Stored XSS in shopware/shopware

## Summary
Severity: Medium
Advisory: GHSA-4p3x-8qw9-24w9
CVE: CVE-2021-41188
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-10-27
Source: https://github.com/advisories/GHSA-4p3x-8qw9-24w9
Type: github-advisory

## Affected
- Packagist: `shopware/shopware` — affected >=0 <5.7.6

## Details
### Impact
Authenticated Stored XSS in Administration

### Patches
Use the Security Plugin:
https://store.shopware.com/en/swag575294366635f/shopware-security-plugin.html

### Workarounds
If you cannot use the security plugin, add the following config to your `.htaccess` file

```
<IfModule mod_headers.c>
    <FilesMatch "\.(?i:svg)$">
        Header set Content-Security-Policy "script-src 'none'"
    </FilesMatch>
</IfModule>
```

If you are using nginx as server config, you can add the following to your configuration:
```
server {
    # ...

    location ~* ^.+\.svg$ {
        add_header Content-Security-Policy "script-src 'none'";
    }
}
```

### References
https://docs.shopware.com/en/shopware-5-en/sicherheitsupdates/security-update-10-2021

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-4p3x-8qw9-24w9
- https://nvd.nist.gov/vuln/detail/CVE-2021-41188
- https://github.com/shopware/shopware/commit/37213e91d525c95df262712cba80d1497e395a58
- https://docs.shopware.com/en/shopware-5-en/sicherheitsupdates/security-update-10-2021
- https://github.com/shopware/shopware
- https://github.com/shopware/shopware/releases/tag/v5.7.6
- https://store.shopware.com/en/swag575294366635f/shopware-security-plugin.html
