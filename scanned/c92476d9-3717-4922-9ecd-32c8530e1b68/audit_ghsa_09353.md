# [H] ssrfcheck: SSRF Bypass Caused by Failure to Classify Reserved IP Address Space as Invalid

## Summary
Severity: High
Advisory: GHSA-p4hc-9pjh-55c8
CVE: CVE-2025-8267
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-p4hc-9pjh-55c8
Type: github-advisory

## Affected
- npm: `ssrfcheck` — affected >=0 <1.2.0

## Details
# SSRF Bypass in `ssrfcheck` - fails to classify reserved IP address space as invalid

`ssrfcheck` is an npm package that serves to provide protection from SSRF by validating URLs or hostname inputs.

Resources: 
 * Project's GitHub code repository: https://github.com/felippe-regazio/ssrfcheck
 * Project's npm package: https://www.npmjs.com/package/ssrfcheck
 
## Vulnerability

The `ssrfcheck` package maintains a denylist of IP addresses and ranges to check against when validating if an IP address is to be considered as safe or not.

However, the IP address list used for the denylist is incomplete and misses a reserved IP address space as defined by the IANA (Internet Assigned Numbers Authority):

- 224.0.0.0/4 - Multicast

Practically, this reserved IP address space is used for multicast traffic and would most commonly be used for reserved local communication over network protocols such as UDP, which would make it less likely to be used in a typical SSRF attack in practice.

However, such reserved IP address space shouldn't be allowed and it would be responsible of the SSRF protection package to align and conform to an agreed-upon standard of special-purposed addresses that should not be considered a valid public IP address. For reference, the popular npm packages `private-ip` and `ipaddr.js` that are highly dependent-upon to make decisions about SSRF protection and both consider the above mentioned IP address space as reserved and is not considered a valid public IP address.

## Exploit Proof of Concept

1. Install the `ssrfcheck` package:

```bash
npm install ssrfcheck
```

2. Define an `app.js` file with the programmatic API of `ssrfcheck`:

```javascript
import { isSSRFSafeURL } from 'ssrfcheck';

let result
result = isSSRFSafeURL('https://012.1.2.3/whatever');
console.log(result);  // returns false
result = isSSRFSafeURL('https://localhost:8080/whatever');
console.log(result);  // returns false

result = isSSRFSafeURL('https://239.255.255.250:8080/whatever');
console.log(result);  // returns true - bypassed
```

## Vulnerable versions

All versions of ssrfcheck are vulnerable to this issue, up to and including to the latest version of `1.1.1`.

## Assigned CVE

[CVE-2025-8267](https://nvd.nist.gov/vuln/detail/CVE-2025-8267)

# Author

Liran Tal

## References
- https://github.com/felippe-regazio/ssrfcheck/security/advisories/GHSA-p4hc-9pjh-55c8
- https://nvd.nist.gov/vuln/detail/CVE-2025-8267
- https://github.com/felippe-regazio/ssrfcheck/issues/5
- https://github.com/felippe-regazio/ssrfcheck/commit/9507b49fd764f2a1a1d1e3b9ee577b7545e6950e
- https://gist.github.com/lirantal/2976840639df824cb3abe60d13c65e04
- https://github.com/felippe-regazio/ssrfcheck
- https://security.snyk.io/vuln/SNYK-JS-SSRFCHECK-9510756
