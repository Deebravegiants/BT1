# [M] Prefect Auth Bypass via endswith() Health Check Exemption

## Summary
Severity: Medium
Advisory: GHSA-6rr6-v7cj-mxpg
CVE: CVE-2026-7722
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-6rr6-v7cj-mxpg
Type: github-advisory

## Affected
- PyPI: `prefect` — affected >=0 <3.6.22

## Details
A vulnerability was detected in PrefectHQ prefect up to 3.6.21. This impacts the function endswith of the file /api/health of the component Health Check API. Performing a manipulation results in improper authentication. The attack is possible to be carried out remotely. The exploit is now public and may be used. Upgrading to version 3.6.22 will fix this issue. Upgrading the affected component is recommended.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7722
- https://github.com/PrefectHQ/prefect/pull/21063
- https://github.com/PrefectHQ/prefect/pull/21063/changes/d8c4ff97ef7c0a940925d32b2d76324c8def42de
- https://github.com/PrefectHQ/prefect/commit/e21617125335025b4b27e7d6f0ca028e8e8f3b79
- https://gist.github.com/nedlir/f576abbb0e491dc9bb7e106c140dda04
- https://github.com/PrefectHQ/prefect
- https://github.com/PrefectHQ/prefect/releases/tag/3.6.22
- https://vuldb.com/submit/807255
- https://vuldb.com/vuln/360898
- https://vuldb.com/vuln/360898/cti
