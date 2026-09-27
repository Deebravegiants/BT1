# [H] dssrf: any users using 1.1.1.1 DNS is impacted by SSRF

## Summary
Severity: High
Advisory: GHSA-5846-7qm3-r52j
CVE: CVE-2026-54729
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-5846-7qm3-r52j
Type: github-advisory

## Affected
- npm: `dssrf` — affected >=0 <1.0.5

## Details
## Summary

is_url_safe can treat localhost as safe when DNS resolver 1.1.1.1 returns NXDOMAIN because dns.resolve4 yields no address and no dns.lookup fallback occurs, allowing server-side request forgery.

## POC

Example to simulate 1.1.1.1 in version before 1.5.0 of dssrf:

```js
import { is_url_safe } from '../dist/helpers.js';
import dns from 'dns';


dns.setServers(['1.1.1.1']);

const TARGET = 'http://localhost/admin';

console.log(`Testing: ${TARGET}`);
console.log(`Current DNS Servers: ${dns.getServers()}`);

const result = await is_url_safe(TARGET);

if (result === true) {
    console.log('dssrf treated localhost as SAFE because 1.1.1.1 returned NXDOMAIN.');
} else {
    console.log('dssrf blocked localhost.');
}
```

## References
- https://github.com/HackingRepo/dssrf-js/security/advisories/GHSA-5846-7qm3-r52j
- https://github.com/HackingRepo/dssrf-js/pull/102
- https://github.com/HackingRepo/dssrf-js/commit/668c21792cd1252baf779a176aa652e2b4c0067d
- https://github.com/HackingRepo/dssrf-js
