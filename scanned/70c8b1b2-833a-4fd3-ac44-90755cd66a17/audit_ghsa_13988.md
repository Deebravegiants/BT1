# [M] Insufficient validation when decoding a Socket.IO packet

## Summary
Severity: Medium
Advisory: GHSA-cqmj-92xf-r6r9
CVE: CVE-2023-32695
CWE: CWE-20, CWE-754
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-05-23
Source: https://github.com/advisories/GHSA-cqmj-92xf-r6r9
Type: github-advisory

## Affected
- npm: `socket.io-parser` — affected >=4.0.4 <4.2.3
- npm: `socket.io-parser` — affected >=3.4.0 <3.4.3
- npm: `socket.io-parser` — affected >=0 <3.3.4

## Details
### Impact

A specially crafted Socket.IO packet can trigger an uncaught exception on the Socket.IO server, thus killing the Node.js process.

```
TypeError: Cannot convert object to primitive value
       at Socket.emit (node:events:507:25)
       at .../node_modules/socket.io/lib/socket.js:531:14
```

### Patches

A fix has been released today (2023/05/22):

- https://github.com/socketio/socket.io-parser/commit/3b78117bf6ba7e99d7a5cfc1ba54d0477554a7f3, included in `socket.io-parser@4.2.3`
- https://github.com/socketio/socket.io-parser/commit/2dc3c92622dad113b8676be06f23b1ed46b02ced, included in `socket.io-parser@3.4.3`


Another fix has been released for the `3.3.x` branch:

- https://github.com/socketio/socket.io-parser/commit/ee006607495eca4ec7262ad080dd3a91439a5ba4, included in `socket.io-parser@3.3.4

| `socket.io` version | `socket.io-parser` version                                                                              | Needs minor update?                  |
|---------------------|---------------------------------------------------------------------------------------------------------|--------------------------------------|
| `4.5.2...latest`    | `~4.2.0` ([ref](https://github.com/socketio/socket.io/commit/9890b036cf942f6b6ad2afeb6a8361c32cd5d528)) | `npm audit fix` should be sufficient |
| `4.1.3...4.5.1`     | `~4.1.1` ([ref](https://github.com/socketio/socket.io/commit/7c44893d7878cd5bba1eff43150c3e664f88fb57)) | Please upgrade to `socket.io@4.6.x`  |
| `3.0.5...4.1.2`     | `~4.0.3` ([ref](https://github.com/socketio/socket.io/commit/752dfe3b1e5fecda53dae899b4a39e6fed5a1a17)) | Please upgrade to `socket.io@4.6.x`  |
| `3.0.0...3.0.4`     | `~4.0.1` ([ref](https://github.com/socketio/socket.io/commit/1af3267e3f5f7884214cf2ca4d5282d620092fb0)) | Please upgrade to `socket.io@4.6.x`  |
| `2.3.0...2.5.0`     | `~3.4.0` ([ref](https://github.com/socketio/socket.io/commit/cf39362014f5ff13a17168b74772c43920d6e4fd)) | `npm audit fix` should be sufficient |


### Workarounds

There is no known workaround except upgrading to a safe version.

### For more information

If you have any questions or comments about this advisory:

- Open a discussion [here](https://github.com/socketio/socket.io/discussions)

Thanks to [@rafax00](https://github.com/rafax00) for the responsible disclosure.

## References
- https://github.com/socketio/socket.io-parser/security/advisories/GHSA-cqmj-92xf-r6r9
- https://nvd.nist.gov/vuln/detail/CVE-2023-32695
- https://github.com/socketio/socket.io-parser/commit/1c220ddbf45ea4b44bc8dbf6f9ae245f672ba1b9
- https://github.com/socketio/socket.io-parser/commit/2dc3c92622dad113b8676be06f23b1ed46b02ced
- https://github.com/socketio/socket.io-parser/commit/3b78117bf6ba7e99d7a5cfc1ba54d0477554a7f3
- https://github.com/socketio/socket.io-parser/commit/ee006607495eca4ec7262ad080dd3a91439a5ba4
- https://github.com/socketio/socket.io-parser
- https://github.com/socketio/socket.io-parser/releases/tag/4.2.3
