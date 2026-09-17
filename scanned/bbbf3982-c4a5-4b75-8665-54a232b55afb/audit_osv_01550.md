# [M] ALPINE-CVE-2019-20446

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-20446
Ecosystem: Alpine:v3.10, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-02-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-20446
Type: osv

## Affected
- Alpine:v3.10: `librsvg` — affected >=2.42.0 <2.40.21-r0
- Alpine:v3.8: `librsvg` — affected >=2.42.0 <2.40.21-r0
- Alpine:v3.9: `librsvg` — affected >=2.42.0 <2.40.21-r0

## Details
In xml.rs in GNOME librsvg before 2.46.2, a crafted SVG file with nested patterns can cause denial of service when passed to the library for processing. The attacker constructs pattern elements so that the number of final rendered objects grows exponentially.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-20446
