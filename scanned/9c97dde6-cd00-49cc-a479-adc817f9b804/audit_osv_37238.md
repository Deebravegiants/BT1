# [H] Samba: group policy certificate enrollment uses http:// without validation

## Summary
Severity: High
Advisory: CVE-2026-3012
CVSS: 8.0 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-3012
Type: osv

## Details
A flaw was found in Samba’s certificate auto-enrollment Group Policy handling. When certificate auto-enrollment is enabled, Samba may retrieve a CA certificate over an unencrypted HTTP connection and install it into the local trust store without proper verification. An attacker with the ability to intercept or redirect network traffic could exploit this behavior to supply a malicious certificate authority certificate, potentially allowing interception or spoofing of trusted communications.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-3012.json
- https://access.redhat.com/errata/RHSA-2026:22644
- https://access.redhat.com/errata/RHSA-2026:22963
- https://access.redhat.com/errata/RHSA-2026:25049
- https://access.redhat.com/errata/RHSA-2026:25979
- https://access.redhat.com/errata/RHSA-2026:28053
- https://access.redhat.com/errata/RHSA-2026:28054
- https://access.redhat.com/errata/RHSA-2026:28055
- https://access.redhat.com/errata/RHSA-2026:28056
- https://access.redhat.com/errata/RHSA-2026:28057
- https://access.redhat.com/errata/RHSA-2026:29863
- https://access.redhat.com/errata/RHSA-2026:56786
- https://access.redhat.com/errata/RHSA-2026:56853
- https://access.redhat.com/errata/RHSA-2026:56911
- https://access.redhat.com/errata/RHSA-2026:57483
- https://access.redhat.com/errata/RHSA-2026:59831
- https://access.redhat.com/errata/RHSA-2026:60019
- https://access.redhat.com/errata/RHSA-2026:62549
- https://access.redhat.com/security/cve/CVE-2026-3012
