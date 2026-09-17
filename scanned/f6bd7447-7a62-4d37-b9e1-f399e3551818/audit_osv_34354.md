# [H] Tautulli vulnerable to Unauthenticated Path Traversal in `/image` endpoint

## Summary
Severity: High
Advisory: CVE-2025-58760
Aliases: GHSA-8g4r-8f3f-hghp
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2025-09-09
Source: https://osv.dev/vulnerability/CVE-2025-58760
Type: osv

## Details
Tautulli is a Python based monitoring and tracking tool for Plex Media Server. The `/image` API endpoint in Tautulli v2.15.3 and earlier is vulnerable to path traversal, allowing unauthenticated attackers to read arbitrary files from the application server's filesystem. In Tautulli, the `/image` API endpoint is used to serve static images from the application's data directory to users. This endpoint can be accessed without authentication, and its intended purpose is for server background images and icons within the user interface. Attackers can exfiltrate files from the application file system, including the `tautulli.db` SQLite database containing active JWT tokens, as well as the `config.ini` file which contains the hashed admin password, the JWT token secret, and the Plex Media Server token and connection details. If the password is cracked, or if a valid JWT token is present in the database, an unauthenticated attacker can escalate their privileges to obtain administrative control over the application. Version 2.16.0 contains a fix for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58760.json
- https://github.com/Tautulli/Tautulli/security/advisories/GHSA-8g4r-8f3f-hghp
- https://nvd.nist.gov/vuln/detail/CVE-2025-58760
- https://github.com/Tautulli/Tautulli/commit/47566128e2e5dde98980d59b7a51b98173bc0b40
