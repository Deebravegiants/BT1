# [C] Lucee RCE/XXE Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-vwjx-mmwm-pwrf
CVE: CVE-2023-38693
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-05
Source: https://github.com/advisories/GHSA-vwjx-mmwm-pwrf
Type: github-advisory

## Affected
- Maven: `org.lucee:lucee` — affected >=5.3.10.79-RC <5.3.12.1
- Maven: `org.lucee:lucee` — affected >=5.4.0.65-RC <5.4.3.2
- Maven: `org.lucee:lucee` — affected >=0
- Maven: `org.lucee:lucee` — affected >=5.3.8.132-RC <5.3.8.236
- Maven: `org.lucee:lucee` — affected >=5.3.9.113 <5.3.9.173

## Details
### Impact

The Lucee team received a responsible disclosure of a security vulnerability which affects all previous releases of Lucee.

After reviewing the report and confirming the vulnerability, the Lucee team then conducted a further security review and found additional vulnerabilities which have been addressed as part of this this security update.

### Patches

Lucee 5.4.3.2 and 5.3.12.1 stable releases have been patched with additional hardening

The older releases, 5.3.7.59., 5.3.8.236 and 5.3.9.173 have also been patched

Any users running older release, should plan to immediately upgrade to the latest stable release

6.0 will have a RC as it's not yet released

## References
- https://github.com/lucee/Lucee/security/advisories/GHSA-vwjx-mmwm-pwrf
- https://nvd.nist.gov/vuln/detail/CVE-2023-38693
- https://github.com/lucee/Lucee
