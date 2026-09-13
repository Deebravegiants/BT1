# [C] CVE-2019-10877

## Summary
Severity: Critical
Advisory: CVE-2019-10877
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-05
Source: https://osv.dev/vulnerability/CVE-2019-10877
Type: osv

## Details
In Teeworlds 0.7.2, there is an integer overflow in CMap::Load() in engine/shared/map.cpp that can lead to a buffer overflow, because multiplication of width and height is mishandled.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00046.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00077.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5KCS2CFDYJFBLZ4QKVPNJWHOZEGQ2LBC/
- https://github.com/teeworlds/teeworlds/issues/2071
