# [C] LaraDashboard: 1-Click Pre-Auth RCE via Host Header + Module Installation Chain

## Summary
Severity: Critical
Advisory: CVE-2025-66509
Aliases: GHSA-j9mm-c9cj-pc82
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-12-04
Source: https://osv.dev/vulnerability/CVE-2025-66509
Type: osv

## Details
LaraDashboard is an all-In-one solution to start a Laravel Application. In 2.3.0 and earlier, the password reset flow trusts the Host header, allowing attackers to redirect the administrator’s reset token to an attacker-controlled server. This can be combined with the module installation process to automatically execute the ServiceProvider::boot() method, enabling arbitrary PHP code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66509.json
- https://github.com/laradashboard/laradashboard/security/advisories/GHSA-j9mm-c9cj-pc82
- https://nvd.nist.gov/vuln/detail/CVE-2025-66509
- https://github.com/laradashboard/laradashboard/commit/cc42f9cdf8e59bce794ee2d812a9709b1e6efa87
