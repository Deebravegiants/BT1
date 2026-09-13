# [H] vproxy Divide by Zero DoS Vulnerability

## Summary
Severity: High
Advisory: GHSA-7h24-c332-p48c
CVE: CVE-2025-54581
CWE: CWE-369
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-07-30
Source: https://github.com/advisories/GHSA-7h24-c332-p48c
Type: github-advisory

## Affected
- crates.io: `vproxy` — affected >=0 <2.4.0

## Details
### Summary
Untrusted, user-controlled data from the HTTP Proxy-Authorization header can induce a denial of service state.

### Details
Untrusted data is extracted from the user-controlled HTTP Proxy-Authorization header and passed to Extension::try_from and flows into parse_ttl_extension where it is parsed as a TTL value. If an attacker supplies a TTL of zero (e.g. by using a username such as 'configuredUser-ttl-0'), the modulo operation 'timestamp % ttl' will cause a division by zero panic, causing the server to crash causing a denial-of-service.

The code assumed to be responsible for this can be found here: https://github.com/0x676e67/vproxy/blob/ab304c3854bf8480be577039ada0228907ba0923/src/extension.rs#L173-L183

### PoC
1. Download and run the latest version of vproxy
2. Send a cUrl request like the following, adjusting address and port as necessary: ```curl -x "http://test-ttl-0:test@127.0.0.1:8101" https://google.com```
3. Wait for a cUrl error indicating "Proxy CONNECT aborted"
4. View logs from the vproxy server
5. Observe that the vproxy server crashed due to a divide-by-zero panic

### Impact
The resulting crash renders the proxy server unusable until it is reset.

Finally, one last note: I'm reporting this on behalf of another researcher at Black Duck. Credit for discovery should be attributed to David Bohannon ([dbohannon](https://github.com/dbohannon))

## References
- https://github.com/0x676e67/vproxy/security/advisories/GHSA-7h24-c332-p48c
- https://nvd.nist.gov/vuln/detail/CVE-2025-54581
- https://github.com/0x676e67/vproxy/commit/aa1bf64c5e7f1c471395f9f29175ffc1b16a1079
- https://github.com/0x676e67/vproxy
- https://github.com/0x676e67/vproxy/releases/tag/v2.4.0
