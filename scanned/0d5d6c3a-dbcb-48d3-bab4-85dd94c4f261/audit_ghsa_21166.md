# [C] Workers for local Dask clusters mistakenly listened on public interfaces

## Summary
Severity: Critical
Advisory: GHSA-hwqr-f3v9-hwxr
CVE: CVE-2021-42343
CWE: CWE-668
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-15
Source: https://github.com/advisories/GHSA-hwqr-f3v9-hwxr
Type: github-advisory

## Affected
- PyPI: `distributed` — affected >=0 <2021.10.0

## Details
Versions of `distributed` earlier than `2021.10.0` had a potential security vulnerability relating to single-machine Dask clusters.

Clusters started with `dask.distributed.LocalCluster` or `dask.distributed.Client()` (which defaults to using `LocalCluster`) would mistakenly configure their respective Dask workers to listen on external interfaces (typically with a randomly selected high port) rather than only on `localhost`. A Dask cluster created using this method AND running on a machine that has these ports exposed could be used by a sophisticated attacker to enable remote code execution. Users running on machines with standard firewalls in place, or using clusters created via cluster objects other than `LocalCluster` (e.g. `dask_kubernetes.KubeCluster`) should not be affected. This vulnerability is documented in CVE-2021-42343, and was fixed in version `2021.10.0` (PR #5427).

## References
- https://github.com/dask/distributed/security/advisories/GHSA-hwqr-f3v9-hwxr
- https://nvd.nist.gov/vuln/detail/CVE-2021-42343
- https://github.com/dask/distributed/pull/5427
- https://github.com/dask/distributed/commit/afce4be8e05fb180e50a9d9e38465f1a82295e1b
- https://docs.dask.org/en/latest/changelog.html
- https://github.com/dask/dask/tags
- https://github.com/dask/distributed
- https://github.com/pypa/advisory-database/tree/main/vulns/distributed/PYSEC-2021-871.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/distributed/PYSEC-2021-872.yaml
