# [H] ALPINE-CVE-2016-5300

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-5300
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-06-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-5300
Type: osv

## Affected
- Alpine:v3.2: `expat` — affected >=0 <2.2.0-r0
- Alpine:v3.3: `expat` — affected >=0 <2.2.0-r0
- Alpine:v3.4: `expat` — affected >=0 <2.2.0-r0

## Details
The XML parser in Expat does not use sufficient entropy for hash initialization, which allows context-dependent attackers to cause a denial of service (CPU consumption) via crafted identifiers in an XML document.  NOTE: this vulnerability exists because of an incomplete fix for CVE-2012-0876.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-5300
