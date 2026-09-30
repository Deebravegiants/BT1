# [M] Default Credentials in nginx-defender Configuration Files

## Summary
Severity: Medium
Advisory: GHSA-pr72-8fxw-xx22
CVE: CVE-2025-55740
CWE: CWE-1392
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-08-19
Source: https://github.com/advisories/GHSA-pr72-8fxw-xx22
Type: github-advisory

## Affected
- Go: `github.com/Anipaleja/nginx-defender` — affected >=0 <1.5.0

## Details
### Impact
This is a configuration vulnerability affecting nginx-defender deployments. Example configuration files 
[config.yaml](https://github.com/Anipaleja/nginx-defender/blob/main/config.yaml), [docker-compose.yml](https://github.com/Anipaleja/nginx-defender/blob/main/docker-compose.yml) contain default credentials (`default_password: "change_me_please"`, `GF_SECURITY_ADMIN_PASSWORD=admin123`). If users deploy nginx-defender without changing these defaults, attackers with network access could gain administrative control, bypassing security protections.

**Who is impacted?**
All users who deploy nginx-defender with default credentials and expose the admin interface to untrusted networks.

### Patches
The issue is addressed in v1.5.0 and later.

Startup warnings are added if default credentials are detected.
Documentation now strongly recommends changing all default passwords before deployment.
Patched versions:
1.5.0 and later
**Will be fully patched in v1.7.0 and later**

### Workarounds
Users can remediate the vulnerability without upgrading by manually changing all default credentials in configuration files before deployment:
```yaml
# config.yaml
auth:
  default_password: "your_strong_password_here"
```

```yml
# docker-compose.yml
- GF_SECURITY_ADMIN_PASSWORD=your_strong_password
```
Restrict access to the admin interface and use environment variables for secrets.

### References
- [Security Configuration Guide](https://github.com/Anipaleja/nginx-defender/blob/main/docs/security-config.md)
- [Full Security Advisory](https://github.com/Anipaleja/nginx-defender/security/advisories)
- [Library README](https://github.com/Anipaleja/nginx-defender/blob/main/lib/README.md)
- [README](https://github.com/Anipaleja/nginx-defender/blob/main/README.md)

## References
- https://github.com/Anipaleja/nginx-defender/security/advisories/GHSA-pr72-8fxw-xx22
- https://nvd.nist.gov/vuln/detail/CVE-2025-55740
- https://github.com/Anipaleja/nginx-defender
- https://pkg.go.dev/vuln/GO-2025-3896
