# [C] WMAgent arbitrary code execution via a crafted dbs-client package

## Summary
Severity: Critical
Advisory: GHSA-4vq7-8699-4xgc
CVE: CVE-2022-34558
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-29
Source: https://github.com/advisories/GHSA-4vq7-8699-4xgc
Type: github-advisory

## Affected
- PyPI: `wmagent` — affected >=1.3.3rc1 <2.0.4
- PyPI: `reqmgr2` — affected >=1.4.0rc2 <2.0.4
- PyPI: `reqmon` — affected >=1.4.1rc5 <2.0.4
- PyPI: `global-workqueue` — affected >=1.4.1rc5 <2.0.4

## Details
WMAgent v1.3.3rc2 and 1.3.3rc1, reqmgr2 1.4.1rc5 and 1.4.0rc2, reqmon 1.4.1rc5, and global-workqueue 1.4.1rc5 allows attackers to execute arbitrary code via a crafted dbs-client package.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34558
- https://github.com/dmwm/WMCore/issues/11188
- https://github.com/dmwm/WMCore
- https://github.com/pypa/advisory-database/tree/main/vulns/global-workqueue/PYSEC-2022-43136.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/reqmon/PYSEC-2022-43163.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/wmagent/PYSEC-2022-43174.yaml
