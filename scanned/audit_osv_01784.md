# [M] ALPINE-CVE-2020-1472

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-1472
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-08-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-1472
Type: osv

## Affected
- Alpine:v3.10: `samba` — affected >=4.11.0 <4.10.18-r0
- Alpine:v3.11: `samba` — affected >=4.11.0 <4.11.14-r0
- Alpine:v3.12: `samba` — affected >=4.11.0 <4.12.7-r0
- Alpine:v3.13: `samba` — affected >=4.11.0 <4.12.7-r0
- Alpine:v3.14: `samba` — affected >=4.11.0 <4.12.7-r0
- Alpine:v3.15: `samba` — affected >=4.11.0 <4.12.7-r0
- Alpine:v3.16: `samba` — affected >=4.11.0 <4.12.7-r0
- Alpine:v3.17: `samba` — affected >=4.11.0 <4.12.7-r0
- Alpine:v3.18: `samba` — affected >=4.11.0 <4.12.7-r0
- Alpine:v3.19: `samba` — affected >=4.11.0 <4.12.7-r0
- Alpine:v3.20: `samba` — affected >=4.11.0 <4.12.7-r0
- Alpine:v3.21: `samba` — affected >=4.11.0 <4.12.7-r0
- Alpine:v3.22: `samba` — affected >=4.11.0 <4.12.7-r0
- Alpine:v3.23: `samba` — affected >=4.11.0 <4.12.7-r0
- Alpine:v3.24: `samba` — affected >=4.11.0 <4.12.7-r0

## Details
An elevation of privilege vulnerability exists when an attacker establishes a vulnerable Netlogon secure channel connection to a domain controller, using the Netlogon Remote Protocol (MS-NRPC). An attacker who successfully exploited the vulnerability could run a specially crafted application on a device on the network.
To exploit the vulnerability, an unauthenticated attacker would be required to use MS-NRPC to connect to a domain controller to obtain domain administrator access.
Microsoft is addressing the vulnerability in a phased two-part rollout. These updates address the vulnerability by modifying how Netlogon handles the usage of Netlogon secure channels.
For guidelines on how to manage the changes required for this vulnerability and more information on the phased rollout, see  How to manage the changes in Netlogon secure channel connections associated with CVE-2020-1472 (updated September 28, 2020).
When the second phase of Windows updates become available in Q1 2021, customers will be notified via a revision to this security vulnerability. If you wish to be notified when these updates are released, we recommend that you register for the security notifications mailer to be alerted of content changes to this advisory. See Microsoft Technical Security Notifications.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-1472
