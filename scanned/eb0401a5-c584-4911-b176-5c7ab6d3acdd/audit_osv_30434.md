# [M] cachi2 allows traceback prints locals

## Summary
Severity: Medium
Advisory: CVE-2024-52582
Aliases: GHSA-w9qc-9m5h-qqmh
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-52582
Type: osv

## Details
Cachi2 is a command-line interface tool that pre-fetches a project's dependencies to aid in making the project's build process network-isolated. Prior to version 0.14.0, secrets may be shown in logs when an unhandled exception is triggered because the tool is logging locals of each function. This may uncover secrets if tool used in CI/build pipelines as it's the main use case. Version 0.14.0 contains a patch for the issue. No known workarounds are available.

## References
- https://typer.tiangolo.com/tutorial/exceptions/?h=#disable-local-variables-for-security
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52582.json
- https://github.com/containerbuildsystem/cachi2/security/advisories/GHSA-w9qc-9m5h-qqmh
- https://nvd.nist.gov/vuln/detail/CVE-2024-52582
- https://github.com/containerbuildsystem/cachi2/commit/d6638e5e14474061a1ab1ba5d0ee72f58b9a11a9
