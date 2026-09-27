# [C] sift 17.1.3 Prototype Pollution Remote Code Execution via $where

## Summary
Severity: Critical
Advisory: CVE-2026-85625
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85625
Type: osv

## Details
sift (sift.js) 17.1.3 enumerates query keys with for...in, which walks the object prototype chain, and dispatches any matched operator key including $where. The $where operation compiles a string value into a function using new Function unless CSP_ENABLED is set (not set by default). As a result, if a prototype-pollution primitive elsewhere in the process sets Object.prototype.$where to a malicious string, even benign filter calls such as sift({}) execute arbitrary JavaScript. Additionally, passing an untrusted query object containing a string $where directly to sift results in code execution under the default configuration.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85625.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85625
- https://www.vulncheck.com/advisories/sift-17.1.3-prototype-pollution-remote-code-execution-via-where
- https://github.com/crcn/sift.js/issues/276
- https://github.com/crcn/sift.js
- https://github.com/crcn/sift.js/blob/v17.1.3/src/core.ts
