# [M] CVE-2024-33903

## Summary
Severity: Medium
Advisory: CVE-2024-33903
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-04-29
Source: https://osv.dev/vulnerability/CVE-2024-33903
Type: osv

## Details
In CARLA through 0.9.15.2, the collision sensor mishandles some situations involving pedestrians or bicycles, in part because the collision sensor function is not exposed to the Blueprint library.

## References
- https://github.com/carla-simulator/carla/blob/60bd026b4822b4edb8a68cc17b9119866f303853/Docs/core_concepts.md
- https://github.com/carla-simulator/carla/tags
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/33xxx/CVE-2024-33903.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-33903
- https://github.com/carla-simulator/carla/issues/7025
- https://github.com/carla-simulator/carla/issues/7394#issuecomment-2058130066
- https://github.com/carla-simulator/carla/pull/7445
