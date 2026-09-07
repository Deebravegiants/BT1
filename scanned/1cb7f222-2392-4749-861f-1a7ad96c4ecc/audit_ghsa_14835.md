# [H] h2o vulnerable to unexpected POST request shutting down server

## Summary
Severity: High
Advisory: GHSA-58m3-rcvp-f9ww
CVE: CVE-2024-5979
CWE: CWE-400, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-06-27
Source: https://github.com/advisories/GHSA-58m3-rcvp-f9ww
Type: github-advisory

## Affected
- PyPI: `h2o` — affected >=0

## Details
In h2oai/h2o-3 version 3.46.0, the `run_tool` command in the `rapids` component allows the `main` function of any class under the `water.tools` namespace to be called. One such class, `MojoConvertTool`, crashes the server when invoked with an invalid argument, causing a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-5979
- https://github.com/h2oai/h2o-3/commit/d0899f8e0f7a584b60405a65b1d7b439aaaa55a5
- https://github.com/h2oai/h2o-3
- https://huntr.com/bounties/d80a2139-fc03-44b7-b739-de41e323b458
