# [M] Mautic does not shield .env files from web traffic

## Summary
Severity: Medium
Advisory: GHSA-h2wg-v8wg-jhxh
CVE: CVE-2024-47056
CWE: CWE-312, CWE-526
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2025-05-28
Source: https://github.com/advisories/GHSA-h2wg-v8wg-jhxh
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=4.4.0 <4.4.16
- Packagist: `mautic/core` — affected >=5.0.0-alpha <5.2.6
- Packagist: `mautic/core` — affected >=6.0.0-alpha <6.0.2

## Details
### Summary 
This advisory addresses a security vulnerability in Mautic where sensitive `.env` configuration files may be directly accessible via a web browser. This exposure could lead to the disclosure of sensitive information, including database credentials, API keys, and other critical system configurations.

Sensitive Information Disclosure via `.env` File Exposure: The `.env` file, which typically contains environment variables and sensitive application configurations, is directly accessible via a web browser due to missing web server configurations that restrict access to such files. This allows an unauthenticated attacker to view the contents of this file by simply navigating to its URL.

### Mitigation
Update Mautic to the latest Mautic version.
By default, Mautic does not use `.env` files for production data.

**For Apache users:** Ensure your web server is configured to respect `.htaccess` files.

**For Nginx users:** As Nginx does not inherently support `.htaccess` files, you must manually add a configuration block to your Nginx server configuration to deny access to `.env` files. Add the following to your Nginx configuration for the Mautic site:

```nginx
location ~ /\.env {
    deny all;
}
```

After modifying your Nginx configuration, remember to reload or restart your Nginx service for the changes to take effect.

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-h2wg-v8wg-jhxh
- https://nvd.nist.gov/vuln/detail/CVE-2024-47056
- https://github.com/mautic/mautic
