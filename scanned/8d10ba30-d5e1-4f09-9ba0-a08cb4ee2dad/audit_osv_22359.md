# [H] Path Traversal in plankanban/planka

## Summary
Severity: High
Advisory: CVE-2022-2653
CVSS: 7.1 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2022-08-04
Source: https://osv.dev/vulnerability/CVE-2022-2653
Type: osv

## Details
With this vulnerability an attacker can read many sensitive files like configuration files, or the /proc/self/environ file, that contains the environment variable used by the web server that includes database credentials. If the web server user is root, an attacker will be able to read any file in the system.

## References
- https://huntr.dev/bounties/5dff7cf9-8bb2-4f67-a02d-b94db5009d70
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/2xxx/CVE-2022-2653.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-2653
- https://github.com/plankanban/planka/commit/ac1df5201dfdaf68d37f7e1b272bc137870d7418
