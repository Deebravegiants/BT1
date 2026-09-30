# [H] CVE-2019-10761

## Summary
Severity: High
Advisory: CVE-2019-10761
Aliases: GHSA-wf5x-cr3r-xr77, SNYK-JS-VM2-473188
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L)
Published: 2022-07-13
Source: https://osv.dev/vulnerability/CVE-2019-10761
Type: osv

## Details
This affects the package vm2 before 3.6.11. It is possible to trigger a RangeError exception from the host rather than the "sandboxed" context by reaching the stack call limit with an infinite recursion. The returned object is then used to reference the mainModule property of the host code running the script allowing it to spawn a child_process and execute arbitrary code.

## References
- https://snyk.io/vuln/SNYK-JS-VM2-473188
- https://github.com/patriksimek/vm2/commit/4b22d704e4794af63a5a2d633385fd20948f6f90
- https://github.com/patriksimek/vm2/issues/197
