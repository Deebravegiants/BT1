# [H] Flower OAuth authentication bypass

## Summary
Severity: High
Advisory: GHSA-q4qm-xhf9-4p8f
CVE: CVE-2022-30034
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2022-06-03
Source: https://github.com/advisories/GHSA-q4qm-xhf9-4p8f
Type: github-advisory

## Affected
- PyPI: `flower` — affected >=0 <1.2.0

## Details
All versions of Flower, a web UI for the Celery Python RPC framework, as of 05-02-2022 are vulnerable to an OAuth authentication bypass. An attacker could then access the Flower API to discover and invoke arbitrary Celery RPC calls or deny service by shutting down Celery task nodes. A fix was released in version 1.2.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-30034
- https://github.com/mher/flower/issues/1217
- https://github.com/mher/flower/pull/1216
- https://github.com/mher/flower
- https://github.com/pypa/advisory-database/tree/main/vulns/flower/PYSEC-2022-42973.yaml
- https://tprynn.github.io/2022/05/26/flower-vulns.html
- http://githubcommherflower.com
