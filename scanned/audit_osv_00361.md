# [M] ALPINE-CVE-2017-1000250

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-1000250
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 6.5 (CVSS:3.0/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-09-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-1000250
Type: osv

## Affected
- Alpine:v3.3: `bluez` — affected >=0 <5.36-r1
- Alpine:v3.4: `bluez` — affected >=0 <5.40-r1
- Alpine:v3.5: `bluez` — affected >=0 <5.42-r1
- Alpine:v3.6: `bluez` — affected >=0 <5.44-r3

## Details
All versions of the SDP server in BlueZ 5.46 and earlier are vulnerable to an information disclosure vulnerability which allows remote attackers to obtain sensitive information from the bluetoothd process memory. This vulnerability lies in the processing of SDP search attribute requests.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-1000250
