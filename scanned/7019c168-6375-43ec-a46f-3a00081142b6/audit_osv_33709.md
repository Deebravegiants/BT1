# [H] Hijacking Caido instance during the initial setup via DNS Rebinding to achieve RCE

## Summary
Severity: High
Advisory: CVE-2025-49004
Aliases: GHSA-jmxf-xw2r-vjrg
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-06-09
Source: https://osv.dev/vulnerability/CVE-2025-49004
Type: osv

## Details
Caido is a web security auditing toolkit. Prior to version 0.48.0, due to the lack of protection for DNS rebinding, Caido can be loaded on an attacker-controlled domain. This allows a malicious website to hijack the authentication flow of Caido and achieve code execution. A malicious website loaded in the browser can hijack the locally running Caido instance and achieve remote command execution during the initial setup. Even if the Caido instance is already configured, an attacker can initiate the authentication flow by performing DNS rebinding. In this case, the victim needs to authorize the request on dashboard.caido.io. Users should upgrade to version 0.48.0 to receive a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49004.json
- https://github.com/caido/caido/security/advisories/GHSA-jmxf-xw2r-vjrg
- https://nvd.nist.gov/vuln/detail/CVE-2025-49004
