# [M] D-Tale Command Execution Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-fg5m-m723-7mv6
CVE: CVE-2024-8862
CWE: CWE-74
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-09-16
Source: https://github.com/advisories/GHSA-fg5m-m723-7mv6
Type: github-advisory

## Affected
- PyPI: `dtale` — affected >=0 <3.14.1

## Details
D-Tale is the combination of a Flask back-end and a React front-end to bring you an easy way to view & analyze Pandas data structures. In dtale\views.py, under the route @dtale.route("/chart-data/<data_id>"), the query parameters from the request are directly passed into run_query for execution. And the run_query function calls proceed without performing any processing or sanitization of the query parameter. As a result, the query is directly used in the df.query method for data retrieval. Tthe engine used is `python`, which allows executing the query expression ans leading to a command execution vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8862
- https://github.com/man-group/dtale/commit/b6e30969390520d1400b55acbb13e5487b8472e8
- https://github.com/man-group/dtale
- https://rumbling-slice-eb0.notion.site/Unauthenticated-Remote-Command-Execution-via-Panda-df-query-9dc40f0477ee4b65806de7921876c222?pvs=4
- https://vuldb.com/?ctiid.277499
- https://vuldb.com/?id.277499
- https://vuldb.com/?submit.403200
