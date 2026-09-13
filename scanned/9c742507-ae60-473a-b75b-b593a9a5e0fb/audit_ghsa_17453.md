# [M] Static Web Server vulnerable to a symbolic link path traversal

## Summary
Severity: Medium
Advisory: GHSA-459f-x8vq-xjjm
CVE: CVE-2025-67487
CWE: CWE-61
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-12-08
Source: https://github.com/advisories/GHSA-459f-x8vq-xjjm
Type: github-advisory

## Affected
- crates.io: `static-web-server` — affected >=0 <2.40.1

## Details
### Summary

Symbolic links (_symlinks_) could be used to access files or directories outside the intended web root folder.

### Details

SWS generally does not prevent symlinks from escaping the web server’s root directory. Therefore, if a malicious actor gains access to the web server’s root directory, they could create symlinks to access other files outside the designated web root folder either by URL or via the directory listing.

### PoC

- Serve a directory (web root) with SWS.
- Create a symlink inside the web root that points to a file outside the web root.
  e.g. `ln -s escape.txt $HOME/.bashrc`
- Open `http://localhost/escape.txt` in your browser.
- The file content will be served.

### Impact

Any web server that runs with elevated privileges (e.g., root/administrator) and handles user-supplied file uploads is primarily impacted.

## References
- https://github.com/static-web-server/static-web-server/security/advisories/GHSA-459f-x8vq-xjjm
- https://nvd.nist.gov/vuln/detail/CVE-2025-67487
- https://github.com/static-web-server/static-web-server/commit/308f0d26ceb9c2c8bd219315d0f53914763357f2
- https://github.com/static-web-server/static-web-server
