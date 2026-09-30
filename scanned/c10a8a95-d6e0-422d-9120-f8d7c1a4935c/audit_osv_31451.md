# [H] Sssd: sssd default kerberos configuration allows privilege escalation on ad-joined linux systems

## Summary
Severity: High
Advisory: CVE-2025-11561
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-09
Source: https://osv.dev/vulnerability/CVE-2025-11561
Type: osv

## Details
A flaw was found in the integration of Active Directory and the System Security Services Daemon (SSSD) on Linux systems. In default configurations, the Kerberos local authentication plugin (sssd_krb5_localauth_plugin) is enabled, but a fallback to the an2ln plugin is possible. This fallback allows an attacker with permission to modify certain AD attributes (such as userPrincipalName or samAccountName) to impersonate privileged users, potentially resulting in unauthorized access or privilege escalation on domain-joined Linux hosts.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://sssd.io/
- https://access.redhat.com/errata/RHSA-2025:19610
- https://access.redhat.com/errata/RHSA-2025:19847
- https://access.redhat.com/errata/RHSA-2025:19848
- https://access.redhat.com/errata/RHSA-2025:19849
- https://access.redhat.com/errata/RHSA-2025:19850
- https://access.redhat.com/errata/RHSA-2025:19851
- https://access.redhat.com/errata/RHSA-2025:19852
- https://access.redhat.com/errata/RHSA-2025:19853
- https://access.redhat.com/errata/RHSA-2025:19854
- https://access.redhat.com/errata/RHSA-2025:19859
- https://access.redhat.com/errata/RHSA-2025:20954
- https://access.redhat.com/errata/RHSA-2025:21020
- https://access.redhat.com/errata/RHSA-2025:21067
- https://access.redhat.com/errata/RHSA-2025:21329
- https://access.redhat.com/errata/RHSA-2025:21795
- https://access.redhat.com/errata/RHSA-2025:22256
- https://access.redhat.com/errata/RHSA-2025:22265
