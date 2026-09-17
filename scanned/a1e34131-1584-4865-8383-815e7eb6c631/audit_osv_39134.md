# [C] Samba: remote code execution in samr

## Summary
Severity: Critical
Advisory: CVE-2026-4408
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-4408
Type: osv

## Details
A flaw was found in Samba. A remote attacker can exploit a misconfiguration in Samba file servers and classic domain controllers that use the "check password script" feature. If this script is configured with the %u substitution character, the client-controlled username is passed without proper escaping of shell meta-characters. This vulnerability allows an attacker to achieve remote command execution on the affected system. This issue primarily affects non-standard configurations where the "check password script" is used with %u and the samba-dcerpcd service is started as a system service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-4408.json
- https://access.redhat.com/errata/RHSA-2026:22644
- https://access.redhat.com/errata/RHSA-2026:22963
- https://access.redhat.com/errata/RHSA-2026:25049
- https://access.redhat.com/errata/RHSA-2026:25979
- https://access.redhat.com/errata/RHSA-2026:28053
- https://access.redhat.com/errata/RHSA-2026:28054
- https://access.redhat.com/errata/RHSA-2026:28055
- https://access.redhat.com/errata/RHSA-2026:28056
- https://access.redhat.com/errata/RHSA-2026:28057
- https://access.redhat.com/errata/RHSA-2026:28058
- https://access.redhat.com/errata/RHSA-2026:28132
- https://access.redhat.com/errata/RHSA-2026:29799
- https://access.redhat.com/errata/RHSA-2026:29833
- https://access.redhat.com/errata/RHSA-2026:29863
- https://access.redhat.com/errata/RHSA-2026:56786
- https://access.redhat.com/errata/RHSA-2026:56853
- https://access.redhat.com/errata/RHSA-2026:56911
- https://access.redhat.com/errata/RHSA-2026:57483
