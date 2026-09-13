# [M] SUCHMOKUO node-worker-threads-pool denial of service Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7vxc-q7rv-qfj8
CVE: CVE-2021-29057
CWE: CWE-400, CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-08-11
Source: https://github.com/advisories/GHSA-7vxc-q7rv-qfj8
Type: github-advisory

## Affected
- npm: `node-worker-threads-pool` — affected >=0

## Details
An issue was discovered in StaticPool in SUCHMOKUO node-worker-threads-pool version 1.4.3 that allows attackers to cause a denial of service.

This can be mitigated by manually creating a timeout. For example:

```ts
const { StaticPool } = require(\"node-worker-threads-pool\");
	
	const staticPool = new StaticPool({
 size: 1,
 task: (n) => {
 while (n) {
 console.log(\"a\");
 }
 return n;
 }
});
 
 staticPool.createExecutor().setTimeout(10).exec(1).then((result) => {
 console.log(\"result from thread pool:\", result);
}).catch(() => console.error('timeout'));
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29057
- https://github.com/SUCHMOKUO/node-worker-threads-pool/issues/20
- https://github.com/SUCHMOKUO/node-worker-threads-pool
