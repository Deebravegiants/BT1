# [M] CVE-2019-14769

## Summary
Severity: Medium
Advisory: CVE-2019-14769
CVSS: 6.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2019-08-08
Source: https://osv.dev/vulnerability/CVE-2019-14769
Type: osv

## Details
Backdrop CMS 1.12.x before 1.12.8 and 1.13.x before 1.13.3 doesn't sufficiently filter output when displaying certain block labels created by administrators. An attacker could potentially craft a specialized label, then have an administrator execute scripting when administering a layout. (This issue is mitigated by the attacker needing permission to create custom blocks on the site, which is typically an administrative permission.)

## References
- https://backdropcms.org/security/backdrop-sa-core-2019-011
