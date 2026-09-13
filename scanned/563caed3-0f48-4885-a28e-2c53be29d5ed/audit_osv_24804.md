# [H] CVE-2023-26919

## Summary
Severity: High
Advisory: CVE-2023-26919
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:L)
Published: 2023-04-10
Source: https://osv.dev/vulnerability/CVE-2023-26919
Type: osv

## Details
delight-nashorn-sandbox 0.2.4 and 0.2.5 is vulnerable to sandbox escape. When allowExitFunctions is set to false, the loadWithNewGlobal function can be used to invoke the exit and quit methods to exit the Java process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/26xxx/CVE-2023-26919.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-26919
- https://github.com/javadelight/delight-nashorn-sandbox/issues/135
