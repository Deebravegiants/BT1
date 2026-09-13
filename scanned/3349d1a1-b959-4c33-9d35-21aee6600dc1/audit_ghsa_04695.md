# [H] AVideo Vulnerable to Unauthenticated .env File Exposure via Official Docker Compose Configuration

## Summary
Severity: High
Advisory: GHSA-wf69-r4mx-43rr
CVE: CVE-2026-33692
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-wf69-r4mx-43rr
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0 <29.0

## Details
## Vulnerability Details

**CWE**: CWE-538 - Insertion of Sensitive Information into Externally-Accessible File or Directory

The official `docker-compose.yml` (line 61) mounts the entire project root directory as the Apache document root:

```yaml
volumes:
  - "./:/var/www/html/AVideo"
```

This causes the `.env` file — which contains database credentials, admin passwords, and infrastructure configuration — to be served as a static file at `/.env`. No `.htaccess` rule or Apache configuration blocks access to dotfiles.

### Exposed Information

An unauthenticated request to `GET /.env` returns:

```
DB_MYSQL_HOST=database
DB_MYSQL_USER=avideo
DB_MYSQL_PASSWORD=avideo
SYSTEM_ADMIN_PASSWORD=admin123
TLS_CERTIFICATE_FILE=/etc/apache2/ssl/localhost.crt
TLS_CERTIFICATE_KEY=/etc/apache2/ssl/localhost.key
NETWORK_SUBNET=172.30.0.0/16
```

## Steps to Reproduce

### Prerequisites
- AVideo deployed using the official `docker-compose.yml`
- No modifications to the default configuration

### Steps
1. Deploy AVideo using `docker compose up -d`
2. Send: `curl http://target/.env`
3. The full `.env` file contents are returned, including database credentials and admin password

## Impact

- **Attacker**: Unauthenticated (any remote user)
- **Victim**: AVideo server and database
- **Specific damage**: Attacker obtains database credentials (`DB_MYSQL_USER`, `DB_MYSQL_PASSWORD`), admin password (`SYSTEM_ADMIN_PASSWORD`), and internal network topology (`NETWORK_SUBNET`). This enables direct database access, admin panel takeover, and further lateral movement within the Docker network.

## Proposed Fix

Add a `.htaccess` rule to block access to dotfiles:

```apache
# Block access to hidden files (.env, .git, etc.)
<FilesMatch "^\.">
    Order Allow,Deny
    Deny from all
</FilesMatch>
```

Or configure Apache to deny dotfile access in the virtual host configuration.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-wf69-r4mx-43rr
- https://github.com/WWBN/AVideo/commit/7f418de1a95ab87bb8c8c3eb3702d71c351e098d
- https://github.com/WWBN/AVideo
