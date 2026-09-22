# [H] Tautulli vulnerable to Unauthenticated Path Traversal in `real_pms_image_proxy`

## Summary
Severity: High
Advisory: CVE-2025-58761
Aliases: GHSA-r732-m675-wj7w
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2025-09-09
Source: https://osv.dev/vulnerability/CVE-2025-58761
Type: osv

## Details
Tautulli is a Python based monitoring and tracking tool for Plex Media Server. The `real_pms_image_proxy` endpoint in Tautulli v2.15.3 and prior is vulnerable to path traversal, allowing unauthenticated attackers to read arbitrary files from the application server's filesystem. The `real_pms_image_proxy` is used to fetch an image directly from the backing Plex Media Server. The image to be fetched is specified through an `img` URL parameter, which can either be a URL or a file path. There is some validation ensuring that `img` begins with the prefix `interfaces/default/images` in order to be served from the local filesystem. However this can be bypassed by passing an `img` parameter which begins with a valid prefix, and then adjoining path traversal characters in order to reach files outside of intended directories. An attacker can exfiltrate files on the application file system, including the `tautulli.db` SQLite database containing active JWT tokens, as well as the `config.ini` file which contains the hashed admin password, the JWT token secret, and the Plex Media Server token and connection details. If the password is cracked, or if a valid JWT token is present in the database, an unauthenticated attacker can escalate their privileges to obtain administrative control over the application. Version 2.16.0 contains a fix for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58761.json
- https://github.com/Tautulli/Tautulli/security/advisories/GHSA-r732-m675-wj7w
- https://nvd.nist.gov/vuln/detail/CVE-2025-58761
- https://github.com/Tautulli/Tautulli/commit/ec77a70aafc555e1aad0d9981f719d1200c117f1
