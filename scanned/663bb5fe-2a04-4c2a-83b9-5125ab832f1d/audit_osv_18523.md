# [C] CVE-2020-28194

## Summary
Severity: Critical
Advisory: CVE-2020-28194
Aliases: GHSA-2m44-rh3c-x4gr
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-01
Source: https://osv.dev/vulnerability/CVE-2020-28194
Type: osv

## Details
Variable underflow exists in accel-ppp radius/packet.c when receiving a RADIUS vendor-specific attribute with length field is less than 2. It has an impact only when the attacker controls the RADIUS server, which can lead to arbitrary code execution.

## References
- https://github.com/accel-ppp/accel-ppp/commit/e9d369aa0054312b7633e964e9f7eb323f1f3d69
- https://github.com/accel-ppp/accel-ppp/security/advisories/GHSA-2m44-rh3c-x4gr
