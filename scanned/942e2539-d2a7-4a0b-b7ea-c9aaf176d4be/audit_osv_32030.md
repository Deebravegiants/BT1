# [C] Coolify Vulnerable to Private Key Hijacking / Remote Command Execution (RCE)

## Summary
Severity: Critical
Advisory: CVE-2025-22609
Aliases: GHSA-3w2c-jfr2-9pg9
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-01-24
Source: https://osv.dev/vulnerability/CVE-2025-22609
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to version 4.0.0-beta.361, the missing authorization allows any authenticated user to attach any existing private key on a coolify instance to his own server. If the server configuration of IP / domain, port (most likely 22) and user (root) matches with the victim's server configuration, then the attacker can use the `Terminal` feature and execute arbitrary commands on the victim's server. Version 4.0.0-beta.361 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22609.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-3w2c-jfr2-9pg9
- https://nvd.nist.gov/vuln/detail/CVE-2025-22609
