# [H] Denial of Service in ethereumjs-vm

## Summary
Severity: High
Advisory: GHSA-2mw7-wggm-m6w3
CVE: CVE-2018-19183
CWE: CWE-119
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-11-21
Source: https://github.com/advisories/GHSA-2mw7-wggm-m6w3
Type: github-advisory

## Affected
- npm: `ethereumjs-vm` — affected >=0

## Details
ethereumjs-vm 2.4.0 allows attackers to cause a denial of service (vm.runCode failure and REVERT) via a "code: Buffer.from(my_code, 'hex')" attribute.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-19183
- https://github.com/ethereumjs/ethereumjs-vm/issues/386
- https://github.com/advisories/GHSA-2mw7-wggm-m6w3
- https://github.com/ethereumjs/ethereumjs-vm
