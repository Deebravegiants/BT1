# [M] Graphite Web Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-3c5x-4hvx-qrrr
CVE: CVE-2022-4728
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-27
Source: https://github.com/advisories/GHSA-3c5x-4hvx-qrrr
Type: github-advisory

## Affected
- PyPI: `graphite-web` — affected >=0

## Details
A vulnerability has been found in Graphite Web and classified as problematic. This vulnerability affects unknown code of the component Cookie Handler. The manipulation leads to cross site scripting. The attack can be initiated remotely. The exploit has been disclosed to the public and may be used. The name of the patch is 2f178f490e10efc03cd1d27c72f64ecab224eb23. It is recommended to apply a patch to fix this issue. VDB-216742 is the identifier assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4728
- https://github.com/graphite-project/graphite-web/issues/2744
- https://github.com/graphite-project/graphite-web/pull/2785
- https://github.com/graphite-project/graphite-web/commit/2f178f490e10efc03cd1d27c72f64ecab224eb23
- https://github.com/graphite-project/graphite-web
- https://vuldb.com/?id.216742
