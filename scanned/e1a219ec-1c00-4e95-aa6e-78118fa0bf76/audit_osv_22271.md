# [H] Malicious users can take over the session of other players

## Summary
Severity: High
Advisory: CVE-2022-24781
Aliases: GHSA-4fv9-g2jh-j5xm
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N)
Published: 2022-03-24
Source: https://osv.dev/vulnerability/CVE-2022-24781
Type: osv

## Details
Geon is a board game based on solving questions about the Pythagorean Theorem. Malicious users can obtain the uuid from other users, spoof that uuid through the browser console and become co-owners of the target session. This issue is patched in version 1.1.0. No known workaround exists.

## References
- https://github.com/math-geon/Geon/releases/tag/v1.1.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24781.json
- https://github.com/math-geon/Geon/security/advisories/GHSA-4fv9-g2jh-j5xm
- https://nvd.nist.gov/vuln/detail/CVE-2022-24781
- https://github.com/math-geon/Geon/commit/005456d752d5434b60026edbc83b2665b8557d19
