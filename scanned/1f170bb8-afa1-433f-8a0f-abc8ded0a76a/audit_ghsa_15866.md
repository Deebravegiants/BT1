# [C] Vendure asset server plugin has local file read vulnerability with AssetServerPlugin & LocalAssetStorageStrategy

## Summary
Severity: Critical
Advisory: GHSA-r9mq-3c9r-fmjq
CVE: CVE-2024-48914
CWE: CWE-20, CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2024-10-15
Source: https://github.com/advisories/GHSA-r9mq-3c9r-fmjq
Type: github-advisory

## Affected
- npm: `@vendure/asset-server-plugin` — affected >=0 <2.3.3
- npm: `@vendure/asset-server-plugin` — affected >=3.0.0 <3.0.5

## Details
# Description

## Path traversal

This vulnerability allows an attacker to craft a request which is able to traverse the server file system and retrieve the contents of arbitrary files, including sensitive data such as configuration files, environment variables, and other critical data stored on the server.

From Rajesh Sharma who discovered the vulnerability:

POC: `curl --path-as-is http://localhost:3000/assets/../package.json` gives you the content of package.json present in the local directory.

The vulnerability stems from usage of decodedReqPath directly in path.join without performing any path normalization i.e path.normalize in node.js

https://github.com/vendure-ecommerce/vendure/blob/801980e8f599c28c5059657a9d85dd03e3827992/packages/asset-server-plugin/src/plugin.ts#L352-L358

If the vendure service is behind some server like nginx, apache, etc. Path normalization is performed on the root server level but still the actual client's request path will be sent to vendure service but not the resultant normalized path. However, depending the type of root server one can try various payloads to bypass such normalization. 

The reporter found a customer website which uses local asset plugin and using above mentioned vulnerability, and was able to find secrets like email credentials.


## DOS via malformed URI

In the same code path is an additional vector for crashing the server via a malformed URI

Again from Rajesh:

There is also a potential Denial of Service (DoS) issue when incorrectly encoded URI characters are passed as part of the asset URL. When these malformed requests are processed, they can lead to system crashes or resource exhaustion, rendering the service unavailable to users.
Exploit: `curl  --path-as-is http://localhost:3000/assets/%80package.json` , here `%80` is not a valid url-encoded character hence the decodeURIComponent is called on it, the entire app crashes. 

```
[:server] /Users/abc/mywork/vendure/packages/asset-server-plugin/src/plugin.ts:353
[:server]         const decodedReqPath = decodeURIComponent(req.path);
[:server]                                ^
[:server] URIError: URI malformed
```

### Patches
v3.0.5, v2.3.3

### Workarounds
- Use object storage rather than the local file system, e.g. MinIO or S3
- Define middleware which detects and blocks requests with urls containing `/../`

## References
- https://github.com/vendure-ecommerce/vendure/security/advisories/GHSA-r9mq-3c9r-fmjq
- https://nvd.nist.gov/vuln/detail/CVE-2024-48914
- https://github.com/vendure-ecommerce/vendure/commit/e2ee0c43159b3d13b51b78654481094fdd4850c5
- https://github.com/vendure-ecommerce/vendure/commit/e4b58af6822d38a9c92a1d8573e19288b8edaa1c
- https://github.com/vendure-ecommerce/vendure
- https://github.com/vendure-ecommerce/vendure/blob/801980e8f599c28c5059657a9d85dd03e3827992/packages/asset-server-plugin/src/plugin.ts#L352-L358
