# [M] netmask npm package mishandles octal input data

## Summary
Severity: Medium
Advisory: GHSA-pch5-whg9-qr2r
CVE: CVE-2021-29418
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-03-29
Source: https://github.com/advisories/GHSA-pch5-whg9-qr2r
Type: github-advisory

## Affected
- npm: `netmask` — affected >=0 <2.0.1

## Details
The netmask package before 2.0.1 for Node.js mishandles certain unexpected characters in an IP address string, such as an octal digit of 9. This (in some situations) allows attackers to bypass access control that is based on IP addresses. NOTE: this issue exists because of an incomplete fix for CVE-2021-28918.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29418
- https://github.com/rs/node-netmask/commit/3f19a056c4eb808ea4a29f234274c67bc5a848f4
- https://security.netapp.com/advisory/ntap-20210604-0001
- https://sick.codes/sick-2021-011
- https://sick.codes/universal-netmask-npm-package-used-by-270000-projects-vulnerable-to-octal-input-data-server-side-request-forgery-remote-file-inclusion-local-file-inclusion-and-more-cve-2021-28918
- https://vuln.ryotak.me/advisories/6
- https://www.npmjs.com/package/netmask
