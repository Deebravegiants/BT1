# [M] ALPINE-CVE-2018-5741

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-5741
Ecosystem: Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-5741
Type: osv

## Affected
- Alpine:v3.6: `bind` — affected >=9.12.0 <9.11.5-r0
- Alpine:v3.7: `bind` — affected >=9.12.0 <9.11.5-r0
- Alpine:v3.8: `bind` — affected >=9.12.0 <9.12.3-r0
- Alpine:v3.9: `bind` — affected >=9.12.0 <9.12.3-r0

## Details
To provide fine-grained controls over the ability to use Dynamic DNS (DDNS) to update records in a zone, BIND 9 provides a feature called update-policy. Various rules can be configured to limit the types of updates that can be performed by a client, depending on the key used when sending the update request. Unfortunately, some rule types were not initially documented, and when documentation for them was added to the Administrator Reference Manual (ARM) in change #3112, the language that was added to the ARM at that time incorrectly described the behavior of two rule types, krb5-subdomain and ms-subdomain. This incorrect documentation could mislead operators into believing that policies they had configured were more restrictive than they actually were. This affects BIND versions prior to BIND 9.11.5 and BIND 9.12.3.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-5741
