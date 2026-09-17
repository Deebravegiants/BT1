# [M] Flarum Vulnerable to Session Hijacking via Authoritative Subdomain Cookie Overwrite

## Summary
Severity: Medium
Advisory: GHSA-hg9j-64wp-m9px
CVE: CVE-2025-27794
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-03-12
Source: https://github.com/advisories/GHSA-hg9j-64wp-m9px
Type: github-advisory

## Affected
- Packagist: `flarum/core` — affected >=0 <1.8.10
- Packagist: `flarum/framework` — affected >=0 <1.8.10

## Details
## **Summary**  
A session hijacking vulnerability exists when an attacker-controlled **authoritative subdomain** under a parent domain (e.g., `subdomain.host.com`) sets cookies scoped to the parent domain (`.host.com`). This allows session token replacement for applications hosted on sibling subdomains (e.g., `community.host.com`) if session tokens aren't rotated post-authentication.  

**Key Constraints**:  
- Attacker must control **any subdomain** under the parent domain (e.g., `evil.host.com` or `x.y.host.com`).  
- Parent domain must **not** be on the [Public Suffix List](https://publicsuffix.org/).

Due to non-existent session token rotation after authenticating we can theoretically reproduce the vulnerability by using browser dev tools, but due to the browser's security measures this does not seem to be exploitable as described.

---

## **Proof of Concept (Deno)**  
```ts
Deno.serve({
    port: 8000, // default
    hostname: 'localhost',
    onListen: (o) => console.log(`Server started at http://${o.hostname}:${o.port}`, o),
  },
  async (req) => (console.log(req), new Response(
    `You've been served! You came from ${req.headers.get('referer')}`,
    {
      //status: 302, // would redirect user to page they came from
      status: 200,
      headers: {
        'set-cookie': 'session_cookie=mytoken; Domain=.deno.dev; Secure; HttpOnly',
        'location': req.headers.get('referer')
      }
    }
  ))
);
```

### **Attack Flow**  
1. **Attacker Setup**: Hosts server at `evil.host.com`.
2. **Harvest Session Token**: Attacker visits `community.host.com` to get a session token for himself to replace the victim's token with his own.
3. **Victim Interaction**: User clicks link to `https://evil.host.com`.  
4. **Cookie Override**: Server sets cookie with `Domain=.host.com` and the harvested token from step 2.  
5. **Session Hijacking**: Victim's future requests to `community.host.com` use attacker's token.  

---

## **Why Reverse DNS Subdomains Fail**  
Browsers block cookie setting for parent domains unless:  
1. **Authoritative Subdomain**: Server must belong to a direct child domain (e.g., `a.host.com`, not `x.y.host.com`).  
2. **Public Suffix Exclusion**: If `host.com` is on the Public Suffix List (e.g., like `github.io`), browsers block cross-subdomain cookies.  

**Example**:  
- ❌ `123.cust.dynamic.host.com` → Cannot set `Domain=.host.com`.  
- ✅ `evil.host.com` → Can set `Domain=.host.com` (if not on PSL).  

---

## **Browser Security Behavior**  
### 1. **Cookie Domain Validation**  
Per [RFC 6265 §5.3](https://datatracker.ietf.org/doc/html/rfc6265#section-5.3):  
> Cookies can only be set for domains the server is authoritative for.  

### 2. **Public Suffix List (PSL)**  
Domains like `host.com` on the PSL trigger browser protections:  
> Subdomains of PSL-listed domains cannot set cookies for parent domains.  

**Verification**:  
- Check PSL status: https://publicsuffix.org/list/  

---

## **Impact**  
- **Account Takeover**: Attacker gains authenticated session access.
- **Data Exposure**: Email, private messages, and other personal data exposed.
- **Exploitable Only If**:  
  - Parent domain is **not** PSL-listed.  
  - Attacker controls **direct child subdomain** (e.g., `evil.host.com`).  

---

## **Remediation**  
1. **Session Token Rotation**:  
   ```ts
   // After authentication:
   invalidateOldSession();
   const newToken = generateToken();
   ```
2. **Cookie Scoping (already in place)**:  
   ```ts
   // Restrict cookies to explicit subdomain:
   "Set-Cookie": "session=token; Domain=community.host.com; Secure; HttpOnly; SameSite=Lax";
   ```
3. **Public Suffix Registration**:  
   Add `host.com` to the Public Suffix List via [PSL Submission](https://publicsuffix.org/submit/).  

---

## **Revised Vulnerability Criteria**  
**Prerequisites**:  
- Attacker controls authoritative subdomain (e.g., `evil.host.com`).  
- Parent domain (`host.com`) is **not** PSL-listed.  
- Session tokens persist post-authentication.  

---

## **References**  
- [RFC 6265: HTTP Cookie Handling](https://tools.ietf.org/html/rfc6265)  
- [Public Suffix List](https://publicsuffix.org/)

## References
- https://github.com/flarum/framework/security/advisories/GHSA-hg9j-64wp-m9px
- https://nvd.nist.gov/vuln/detail/CVE-2025-27794
- https://github.com/flarum/framework/commit/a05aaea3ee1e0a8b870935183193cd6052f1d402
- https://github.com/flarum/framework
- https://github.com/flarum/framework/releases/tag/v1.8.10
