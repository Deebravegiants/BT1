# [M] ReDoS in Sec-Websocket-Protocol header

## Summary
Severity: Medium
Advisory: GHSA-6fc8-4gx4-v693
CVE: CVE-2021-32640
CWE: CWE-345, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2021-05-28
Source: https://github.com/advisories/GHSA-6fc8-4gx4-v693
Type: github-advisory

## Affected
- npm: `ws` — affected >=7.0.0 <7.4.6
- npm: `ws` — affected >=6.0.0 <6.2.2
- npm: `ws` — affected >=5.0.0 <5.2.3

## Details
### Impact

A specially crafted value of the `Sec-Websocket-Protocol` header can be used to significantly slow down a ws server.

### Proof of concept

```js
for (const length of [1000, 2000, 4000, 8000, 16000, 32000]) {
  const value = 'b' + ' '.repeat(length) + 'x';
  const start = process.hrtime.bigint();

  value.trim().split(/ *, */);

  const end = process.hrtime.bigint();

  console.log('length = %d, time = %f ns', length, end - start);
}
```

### Patches

The vulnerability was fixed in ws@7.4.6 (https://github.com/websockets/ws/commit/00c425ec77993773d823f018f64a5c44e17023ff) and backported to ws@6.2.2 (https://github.com/websockets/ws/commit/78c676d2a1acefbc05292e9f7ea0a9457704bf1b) and ws@5.2.3 (https://github.com/websockets/ws/commit/76d47c1479002022a3e4357b3c9f0e23a68d4cd2).

### Workarounds

In vulnerable versions of ws, the issue can be mitigated by reducing the maximum allowed length of the request headers using the [`--max-http-header-size=size`](https://nodejs.org/api/cli.html#cli_max_http_header_size_size) and/or the [`maxHeaderSize`](https://nodejs.org/api/http.html#http_http_createserver_options_requestlistener) options.

### Credits

The vulnerability was responsibly disclosed along with a fix in private by [Robert McLaughlin](https://github.com/robmcl4) from University of California, Santa Barbara.

## References
- https://github.com/websockets/ws/security/advisories/GHSA-6fc8-4gx4-v693
- https://nvd.nist.gov/vuln/detail/CVE-2021-32640
- https://github.com/websockets/ws/issues/1895
- https://github.com/websockets/ws/commit/00c425ec77993773d823f018f64a5c44e17023ff
- https://github.com/websockets/ws
- https://lists.apache.org/thread.html/rdfa7b6253c4d6271e31566ecd5f30b7ce1b8fb2c89d52b8c4e0f4e30@%3Ccommits.tinkerpop.apache.org%3E
- https://security.netapp.com/advisory/ntap-20210706-0005
