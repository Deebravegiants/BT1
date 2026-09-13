# [M] ALPINE-CVE-2016-3120

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-3120
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-08-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-3120
Type: osv

## Affected
- Alpine:v3.2: `krb5` — affected >=0 <1.13.6-r0
- Alpine:v3.3: `krb5` — affected >=0 <1.14.3-r0
- Alpine:v3.4: `krb5` — affected >=0 <1.14.3-r0

## Details
The validate_as_request function in kdc_util.c in the Key Distribution Center (KDC) in MIT Kerberos 5 (aka krb5) before 1.13.6 and 1.4.x before 1.14.3, when restrict_anonymous_to_tgt is enabled, uses an incorrect client data structure, which allows remote authenticated users to cause a denial of service (NULL pointer dereference and daemon crash) via an S4U2Self request.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-3120
