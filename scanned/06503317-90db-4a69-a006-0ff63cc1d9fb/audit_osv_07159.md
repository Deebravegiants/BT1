# [H] BIT-node-2025-23083

## Summary
Severity: High
Advisory: BIT-node-2025-23083
Aliases: BIT-node-min-2025-23083, CVE-2025-23083
Ecosystem: Bitnami
Published: 2025-01-27
Source: https://osv.dev/vulnerability/BIT-node-2025-23083
Type: osv

## Affected
- Bitnami: `node` — affected >=23.0.0 <23.8.0

## Details
With the aid of the diagnostics_channel utility, an event can be hooked into whenever a worker thread is created. This is not limited only to workers but also exposes internal workers, where an instance of them can be fetched, and its constructor can be grabbed and reinstated for malicious usage. 

This vulnerability affects Permission Model users (--permission) on Node.js v20, v22, and v23.

## References
- https://nodejs.org/en/blog/vulnerability/january-2025-security-releases
- https://security.netapp.com/advisory/ntap-20250228-0008/
- https://nvd.nist.gov/vuln/detail/CVE-2025-23083
- https://www.vicarius.io/vsociety/posts/cve-2025-23083-detect-nodejs-vulnerability
- https://www.vicarius.io/vsociety/posts/cve-2025-23083-mitigate-nodejs-vulnerability
