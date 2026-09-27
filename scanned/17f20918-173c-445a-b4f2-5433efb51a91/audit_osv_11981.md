# [M] CVE-2018-1000524

## Summary
Severity: Medium
Advisory: CVE-2018-1000524
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-06-26
Source: https://osv.dev/vulnerability/CVE-2018-1000524
Type: osv

## Details
miniSphere version 5.2.9 and earlier contains a Integer Overflow vulnerability in layer_resize() function in map_engine.c that can result in remote denial of service. This attack appear to be exploitable via the victim must load a specially-crafted map which calls SetLayerSize in its entry script. This vulnerability appears to have been fixed in 5.0.3, 5.1.5, 5.2.10 and later.

## References
- https://github.com/fatcerberus/minisphere/pull/268
- https://github.com/fatcerberus/minisphere/commit/252c1ca184cb38e1acb917aa0e451c5f08519996
