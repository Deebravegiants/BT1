# [H] Incomplete mitigation of CVE-2026-4519, %action expansion for command injection to webbrowser.open()

## Summary
Severity: High
Advisory: BIT-libpython-2026-4786
Aliases: BIT-python-2026-4786, BIT-python-min-2026-4786, CVE-2026-4786, PSF-0000-CVE-2026-4786, PSF-2026-17
Ecosystem: Bitnami
Published: 2026-07-06
Source: https://osv.dev/vulnerability/BIT-libpython-2026-4786
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.14.0 <3.14.5

## Details
Mitgation of CVE-2026-4519 was incomplete. If the URL contained "%action" the mitigation could be bypassed for certain browser types the "webbrowser.open()" API could have commands injected into the underlying shell. See CVE-2026-4519 for details.

## References
- https://access.redhat.com/errata/RHSA-2026:10117
- https://access.redhat.com/errata/RHSA-2026:10140
- https://access.redhat.com/errata/RHSA-2026:10141
- https://access.redhat.com/errata/RHSA-2026:10711
- https://access.redhat.com/errata/RHSA-2026:10745
- https://access.redhat.com/errata/RHSA-2026:10774
- https://access.redhat.com/errata/RHSA-2026:10949
- https://access.redhat.com/errata/RHSA-2026:10950
- https://access.redhat.com/errata/RHSA-2026:11062
- https://access.redhat.com/errata/RHSA-2026:11077
- https://access.redhat.com/errata/RHSA-2026:11768
- https://access.redhat.com/errata/RHSA-2026:13692
- https://access.redhat.com/errata/RHSA-2026:13812
- https://access.redhat.com/errata/RHSA-2026:14652
- https://access.redhat.com/errata/RHSA-2026:14653
- https://access.redhat.com/errata/RHSA-2026:14656
- https://access.redhat.com/errata/RHSA-2026:16699
- https://access.redhat.com/errata/RHSA-2026:17525
- https://access.redhat.com/errata/RHSA-2026:17619
- https://access.redhat.com/errata/RHSA-2026:19019
