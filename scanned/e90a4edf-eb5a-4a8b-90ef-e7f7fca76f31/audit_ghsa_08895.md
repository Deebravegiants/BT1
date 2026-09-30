# [H] axios's shouldBypassProxy does not recognize IPv4-mapped IPv6 addresses, allowing NO_PROXY bypass (incomplete fix for CVE-2025-62718)

## Summary
Severity: High
Advisory: GHSA-pjwm-pj3p-43mv
CVE: CVE-2026-44492
CWE: CWE-289, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-pjwm-pj3p-43mv
Type: github-advisory

## Affected
- npm: `axios` — affected >=1.15.0 <1.16.0
- npm: `axios` — affected >=0 <0.32.0

## Details
### Summary
shouldBypassProxy, introduced in v1.15.0 to fix CVE-2025-62718, does not normalise IPv4-mapped IPv6 addresses. When NO_PROXY lists an IPv4 address such as `127.0.0.1` or `169.254.169.254`, a request URL using the IPv4-mapped IPv6 form (`::ffff:7f00:1`, `::ffff:a9fe:a9fe`) still routes through the configured proxy. Node.js resolves these addresses to the underlying IPv4 host, so the request reaches the internal service via the proxy rather than being blocked.

### Details
lib/helpers/shouldBypassProxy.js (v1.15.0):                                                                                                                                   

```javascript                                                                                                                                                                              
  const LOOPBACK_ADDRESSES = new Set(['localhost', '127.0.0.1', '::1']);                                                                                                      
  const isLoopback = (host) => LOOPBACK_ADDRESSES.has(host);                                                                                                                    
                                                                                                                                                                                
  // normalizeNoProxyHost strips brackets and trailing dots, but not ::ffff: prefix                                                                                             
  return hostname === entryHost || (isLoopback(hostname) && isLoopback(entryHost));                                                                                             
```
                                                                                                                                                                                
The WHATWG URL parser canonicalises `http://[::ffff:127.0.0.1]/` to hostname `[::ffff:7f00:1]`. After bracket-stripping: `::ffff:7f00:1`. This string does not match 127.0.0.1 in NO_PROXY and is not in LOOPBACK_ADDRESSES, so shouldBypassProxy returns false and the proxy is used.  proxy-from-env (called before shouldBypassProxy) has the same gap - it does not equate ::ffff:7f00:1 with 127.0.0.1 - so neither layer catches the bypass.

### PoC
```javascript

// NO_PROXY=127.0.0.1,localhost,::1  HTTP_PROXY=http://attacker:8080
import shouldBypassProxy from 'axios/lib/helpers/shouldBypassProxy.js';                                                                                                       
                                                                                                                                                                              
// All three should return true (bypass proxy). Only the first two do.                                                                                                        
console.log(shouldBypassProxy('http://127.0.0.1/'));          // true  [OK]                                                                                                     
console.log(shouldBypassProxy('http://[::1]/'));               // true  [OK]                                                                                                     
console.log(shouldBypassProxy('http://[::ffff:127.0.0.1]/')); // false <- bypass                                                                                             
console.log(shouldBypassProxy('http://[::ffff:7f00:1]/'));     // false <- bypass

```                                                                                              
                                                                                                                                                                              
Node.js routes ::ffff:7f00:1 to 127.0.0.1:                                                                                                                                    

```                                                                                                                                                                              
// net.connect({ host: '::ffff:7f00:1', port: 80 }) reaches a service                                                                                                       
// bound to 127.0.0.1:80 — confirmed on Node.js v24, Linux and macOS.                                                                                                         
```                                                                                                                                                                              
Cloud metadata SSRF: ::ffff:a9fe:a9fe = ::ffff:169.254.169.254. If NO_PROXY=169.254.169.254 is set to block IMDS access, a request to http://[::ffff:a9fe:a9fe]/latest/meta-data/ bypasses it.                                                                                                                      
                                                                                                                                                                            
#### Fix                                                                                                                                                                           
                                                                                                                                                                            
Canonicalise IPv4-mapped IPv6 in normalizeNoProxyHost before any comparison:                                                                                                  
 
 ```javascript                                                                                                                                                                           
const ipv4MappedDotted = /^::ffff:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$/i;                                                                                                    
const ipv4MappedHex    = /^::ffff:([0-9a-f]{1,4}):([0-9a-f]{1,4})$/i;                                                                                                         
                                                                                                                                                                              
function hexToIPv4(a, b) {                                                                                                                                                    
  const hi = parseInt(a, 16), lo = parseInt(b, 16);                                                                                                                           
  return `${hi >> 8}.${hi & 0xff}.${lo >> 8}.${lo & 0xff}`;                                                                                                                   
}                                                                                                                                                                             
                                                                                                                                                                              
const normalizeNoProxyHost = (hostname) => {                                                                                                                                  
  if (!hostname) return hostname;                                                                                                                                           
  if (hostname[0] === '[' && hostname.at(-1) === ']')
    hostname = hostname.slice(1, -1);                                                                                                                                         
  hostname = hostname.replace(/\.+$/, '').toLowerCase();
                                                                                                                                                                              
  let m;                                                                                                                                                                    
  if ((m = hostname.match(ipv4MappedDotted))) return m[1];                                                                                                                    
  if ((m = hostname.match(ipv4MappedHex)))    return hexToIPv4(m[1], m[2]);                                                                                                   
  return hostname;                                                                                                                                                            
};

```

### Impact
Any application that sets NO_PROXY to exclude internal or metadata endpoints and uses an HTTP/HTTPS proxy can have those exclusions bypassed by a URL using IPv4-mapped IPv6 notation. The attacker must control the request URL. In cloud environments with instance metadata services, this can lead to credential exfiltration.

## References
- https://github.com/axios/axios/security/advisories/GHSA-pjwm-pj3p-43mv
- https://nvd.nist.gov/vuln/detail/CVE-2026-44492
- https://nvd.nist.gov/vuln/detail/CVE-2025-62718
- https://access.redhat.com/errata/RHSA-2026:36611
- https://access.redhat.com/errata/RHSA-2026:36754
- https://access.redhat.com/errata/RHSA-2026:36820
- https://access.redhat.com/errata/RHSA-2026:36882
- https://access.redhat.com/errata/RHSA-2026:36883
- https://access.redhat.com/errata/RHSA-2026:40119
- https://access.redhat.com/errata/RHSA-2026:40138
- https://access.redhat.com/errata/RHSA-2026:40262
- https://access.redhat.com/errata/RHSA-2026:41031
- https://access.redhat.com/errata/RHSA-2026:41055
- https://access.redhat.com/errata/RHSA-2026:41064
- https://access.redhat.com/errata/RHSA-2026:41066
- https://access.redhat.com/security/cve/CVE-2026-44492
- https://bugzilla.redhat.com/show_bug.cgi?id=2487938
- https://github.com/axios/axios
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-44492.json
- https://access.redhat.com/errata/RHSA-2026:20889
