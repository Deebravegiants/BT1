# [C] n8n Vulnerable to RCE via Arbitrary File Write

## Summary
Severity: Critical
Advisory: GHSA-v364-rw7m-3263
CVE: CVE-2026-21877
CWE: CWE-434
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-06
Source: https://github.com/advisories/GHSA-v364-rw7m-3263
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0.123.0 <1.121.3

## Details
### Impact
n8n is affected by an authenticated Remote Code Execution (RCE) vulnerability.

Under certain conditions, an authenticated user may be able to cause untrusted code to be executed by the n8n service. This could result in full compromise of the affected instance.

Both self-hosted and n8n Cloud instances are impacted.

### Patches
The issue has been resolved in n8n version 1.121.3.

Users are advised to upgrade to this version or later to fully address the vulnerability.

### Workarounds
If upgrading is not immediately possible, administrators can reduce exposure by disabling the Git node and limiting access for untrusted users.

### References
- n8n documentation: [Blocking access to nodes](https://docs.n8n.io/hosting/securing/blocking-nodes/)

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-v364-rw7m-3263
- https://github.com/n8n-io/n8n
