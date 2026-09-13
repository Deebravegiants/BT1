# [M] ALPINE-CVE-2021-41157

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-41157
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-10-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-41157
Type: osv

## Affected
- Alpine:v3.15: `freeswitch` — affected >=0 <1.10.7-r0
- Alpine:v3.16: `freeswitch` — affected >=0 <1.10.7-r0
- Alpine:v3.17: `freeswitch` — affected >=0 <1.10.7-r0
- Alpine:v3.18: `freeswitch` — affected >=0 <1.10.7-r0
- Alpine:v3.19: `freeswitch` — affected >=0 <1.10.7-r0
- Alpine:v3.20: `freeswitch` — affected >=0 <1.10.7-r0
- Alpine:v3.21: `freeswitch` — affected >=0 <1.10.7-r0
- Alpine:v3.22: `freeswitch` — affected >=0 <1.10.7-r0
- Alpine:v3.23: `freeswitch` — affected >=0 <1.10.7-r0
- Alpine:v3.24: `freeswitch` — affected >=0 <1.10.7-r0

## Details
FreeSWITCH is a Software Defined Telecom Stack enabling the digital transformation from proprietary telecom switches to a software implementation that runs on any commodity hardware. By default, SIP requests of the type SUBSCRIBE are not authenticated in the affected versions of FreeSWITCH. Abuse of this security issue allows attackers to subscribe to user agent event notifications without the need to authenticate. This abuse poses privacy concerns and might lead to social engineering or similar attacks. For example, attackers may be able to monitor the status of target SIP extensions. Although this issue was fixed in version v1.10.6, installations upgraded to the fixed version of FreeSWITCH from an older version, may still be vulnerable if the configuration is not updated accordingly. Software upgrades do not update the configuration by default. SIP SUBSCRIBE messages should be authenticated by default so that FreeSWITCH administrators do not need to explicitly set the `auth-subscriptions` parameter. When following such a recommendation, a new parameter can be introduced to explicitly disable authentication.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-41157
