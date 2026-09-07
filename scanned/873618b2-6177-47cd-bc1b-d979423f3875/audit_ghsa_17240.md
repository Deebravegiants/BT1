# [M] hemmelig allows SSRF Filter bypass via Secret Request functionality

## Summary
Severity: Medium
Advisory: GHSA-vvxf-wj5w-6gj5
CVE: CVE-2025-69206
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-12-29
Source: https://github.com/advisories/GHSA-vvxf-wj5w-6gj5
Type: github-advisory

## Affected
- npm: `hemmelig` — affected >=0 <7.3.3

## Details
### Summary
A Server-Side Request Forgery (SSRF) filter bypass vulnerability exists in the webhook URL validation of the Secret Requests feature. The application attempts to block internal/private IP addresses but can be bypassed using DNS rebinding (e.g., `localtest.me` which resolves to `127.0.0.1`) or open redirect services (e.g., `httpbin.org/redirect-to`). This allows an authenticated user to make the server initiate HTTP requests to internal network resources.

### Details
The vulnerability exists in the `isPublicUrl` function located in `/api/lib/utils.ts`. The function validates webhook URLs against a blocklist of private IP patterns:

```typescript
export const isPublicUrl = (url: string): boolean => {
    const parsed = new URL(url);
    const hostname = parsed.hostname.toLowerCase();
    
    const blockedPatterns = [
        /^localhost$/,
        /^127\.\d{1,3}\.\d{1,3}\.\d{1,3}$/,
        /^192\.168\.\d{1,3}\.\d{1,3}$/,
        // ... other patterns
    ];
    
    return !blockedPatterns.some((pattern) => pattern.test(hostname));
};
```

**The validation is flawed because:**

1. **DNS Rebinding Bypass**: It only checks the hostname string, not the resolved IP address. Domains like `localtest.me` pass validation (not matching any blocked pattern) but resolve to `127.0.0.1`.

2. **Open Redirect Bypass**: External URLs like `httpbin.org/redirect-to?url=http://127.0.0.1` pass validation since `httpbin.org` is a public domain. When the server follows the redirect, it connects to the internal address.

### PoC
Optional: On the container that runs Hemmelig application, host a temporary port with the following command: 
```
node -e "require('http').createServer((req,res)=>{console.log(req.method,req.url,req.headers);res.end('ok')}).listen(8080,()=>console.log('Listening on 8080'))"
```
1. Log in as an user
2. Switch to `Secret Requests` tab and create a new request
3. When inside the request dialog, there are 2 possible payloads that can be used on the `Webhook URL` input to bypass SSRF
```
1. Using domain redirect: http://localtest.me:PORT
2. Using httpbin to perform a redirect: httpbin.org/redirect-to?url=http://127.0.0.1:PORT
```
4. Open a new browser/tab and confirm the request by creating a secret. Upon clicking save, the port we hosted we receive a request. 
<img width="795" height="310" alt="image" src="https://github.com/user-attachments/assets/95d559e5-ead2-4b5d-8e53-9ddec3416953" />

Otherwise, if the port doesn't exist, a similar error in the logs can be found:
```
Secret request webhook delivery failed after retries: TypeError: fetch failed
    at node:internal/deps/undici/undici:15845:13
    at process.processTicksAndRejections (node:internal/process/task_queues:103:5)
    at async sendSecretRequestWebhook (/app/api/routes/secret-requests.ts:58:34) {
  [cause]: Error: connect ECONNREFUSED 127.0.0.1:80
      at TCPConnectWrap.afterConnect [as oncomplete] (node:net:1637:16) {
    errno: -111,
    code: 'ECONNREFUSED',
    syscall: 'connect',
    address: '127.0.0.1',
    port: 80
  }
}
```
### Impact
While the SSRF filter can be bypassed, the practical impact is limited because this is a Blind SSRF, there is no response reflected. But with certain technique like response-timing, the attackers can still indicate whether or not a port is opened.

### Remediation
Replace hostname-based validation with IP resolution checking:
```typescript
import { isIP } from 'is-ip';
import dns from 'dns/promises';

export const isPublicUrl = async (url: string): Promise<boolean> => {
    const parsed = new URL(url);
    const hostname = parsed.hostname;
    
    // Resolve hostname to IP
    let addresses: string[];
    try {
        if (isIP(hostname)) {
            addresses = [hostname];
        } else {
            addresses = await dns.resolve4(hostname).catch(() => []);
            const ipv6 = await dns.resolve6(hostname).catch(() => []);
            addresses = [...addresses, ...ipv6];
        }
    } catch {
        return false;
    }
    
    // Check resolved IPs against blocklist
    const privateRanges = [
        /^127\./,
        /^10\./,
        /^192\.168\./,
        /^172\.(1[6-9]|2\d|3[0-1])\./,
        /^169\.254\./,
        /^::1$/,
        /^fe80:/i,
        /^fc00:/i,
        /^fd/i,
    ];
    
    return addresses.length > 0 && !addresses.some(ip => 
        privateRanges.some(pattern => pattern.test(ip))
    );
};
```
Additionally, disable following redirects in the webhook fetch call or re-validate the URL after each redirect.

## References
- https://github.com/HemmeligOrg/Hemmelig.app/security/advisories/GHSA-vvxf-wj5w-6gj5
- https://nvd.nist.gov/vuln/detail/CVE-2025-69206
- https://github.com/HemmeligOrg/Hemmelig.app/commit/6c909e571d0797ee3bbd2c72e4eb767b57378228
- https://github.com/HemmeligOrg/Hemmelig.app
