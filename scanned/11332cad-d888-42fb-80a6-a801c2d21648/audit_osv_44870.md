# [C] bestzip 2.2.6 and 3.0.2 Argument Injection via the Native Zip Destination

## Summary
Severity: Critical
Advisory: CVE-2026-87794
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-87794
Type: osv

## Details
bestzip versions 2.2.6 and 3.0.2 contain an argument injection vulnerability in the nativeZip function that allows attackers to inject arbitrary arguments to the Info-ZIP backend. Attackers can supply a malicious destination path combined with crafted source entries to execute arbitrary commands with Node.js process privileges. Fixed in 2.2.7 and 3.0.3.

## References
- https://www.npmjs.com/package/bestzip
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87794.json
- https://github.com/nfriedly/node-bestzip/security/advisories/GHSA-p87m-9567-rgcc
- https://github.com/nfriedly/node-bestzip/security/advisories/GHSA-xhwx-rch4-ph2v
- https://nvd.nist.gov/vuln/detail/CVE-2026-87794
- https://www.vulncheck.com/advisories/bestzip-2.2.6-and-3.0.2-argument-injection-via-the-native-zip-destination
- https://github.com/nfriedly/node-bestzip/commit/2adb637b0acb05b8475de7db5af4b86ffcf40aaf
- https://github.com/nfriedly/node-bestzip
- https://github.com/nfriedly/node-bestzip/blob/v3.0.2/lib/bestzip.js
