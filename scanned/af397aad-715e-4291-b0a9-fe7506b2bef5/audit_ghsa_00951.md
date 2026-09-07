# [M] Potential XSS in jQuery dependency in Mirador

## Summary
Severity: Medium
Advisory: GHSA-hgwm-pv9h-q5m7
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-18
Source: https://github.com/advisories/GHSA-hgwm-pv9h-q5m7
Type: github-advisory

## Affected
- npm: `mirador` — affected >=0 <3.0.0-alpha.0

## Details
### Impact
Mirador users less than v3.0.0 (alpha-rc) versions that have an unpatched jQuery. When adopters update jQuery they will find some of Mirador functionality to be broken.

### Patches
Mirador adopters should update to v3.0.0, no updates exist for v2.x releases.

### Workarounds
Yes, Mirador users could fork and create their own custom build of Mirador and make the bug fixes themselves.

### References
https://github.com/advisories/GHSA-gxr4-xjj5-5px2
https://github.com/advisories/GHSA-jpcq-cgw6-v4j6


https://blog.jquery.com/2020/04/10/jquery-3-5-0-released/
https://jquery.com/upgrade-guide/3.5/

## References
- https://github.com/ProjectMirador/mirador/security/advisories/GHSA-hgwm-pv9h-q5m7
- https://github.com/ProjectMirador/mirador
