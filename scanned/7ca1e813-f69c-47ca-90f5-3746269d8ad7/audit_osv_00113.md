# [H] ALPINE-CVE-2016-4477

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-4477
Ecosystem: Alpine:v3.4
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-05-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-4477
Type: osv

## Affected
- Alpine:v3.4: `wpa_supplicant` — affected >=0 <2.5-r3

## Details
wpa_supplicant 0.4.0 through 2.5 does not reject \n and \r characters in passphrase parameters, which allows local users to trigger arbitrary library loading and consequently gain privileges, or cause a denial of service (daemon outage), via a crafted (1) SET, (2) SET_CRED, or (3) SET_NETWORK command.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-4477
