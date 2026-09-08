# [M] lobe-chat has an Open Redirect

## Summary
Severity: Medium
Advisory: GHSA-xph5-278p-26qx
CVE: CVE-2025-59426
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-09-24
Source: https://github.com/advisories/GHSA-xph5-278p-26qx
Type: github-advisory

## Affected
- npm: `@lobehub/chat` — affected >=0 <1.130.1

## Details
### **Description**

---

> Vulnerability Overview
> 

The project's OIDC redirect handling logic constructs the host and protocol of the final redirect URL based on the X-Forwarded-Host or Host headers and the X-Forwarded-Proto value. In deployments where a reverse proxy forwards client-supplied X-Forwarded-* headers to the origin as-is, or where the origin trusts them without validation, an attacker can inject an arbitrary host and trigger an open redirect that sends users to a malicious domain.

> Vulnerable Code Analysis
> 

```bash
const internalRedirectUrlString = await oidcService.getInteractionResult(uid, result);
log('OIDC Provider internal redirect URL string: %s', internalRedirectUrlString);

let finalRedirectUrl;
try {
  finalRedirectUrl = correctOIDCUrl(request, new URL(internalRedirectUrlString));
} catch {
  finalRedirectUrl = new URL(internalRedirectUrlString);
  log('Warning: Could not parse redirect URL, using as-is: %s', internalRedirectUrlString);
}

return NextResponse.redirect(finalRedirectUrl, {
  headers: request.headers,
  status: 303,
});
```

https://github.com/lobehub/lobe-chat/blob/aa841a3879c30142720485182ad62aa0dbd74edc/src/app/(backend)/oidc/consent/route.ts#L113-L127

### PoC

---

> curl Example
> 

```bash
curl -i 'http://localhost:3210/oidc/callback/desktop?code=abc&state=test123' \
  -H 'X-Forwarded-Host: google.com' \
  -H 'X-Forwarded-Proto: https'
```

<img width="1504" height="304" alt="image" src="https://github.com/user-attachments/assets/b71d937d-7be2-49db-8f3d-e07371912800" />


### Impact

---

- It can force users to redirect to untrusted external domains, leading to subsequent attacks such as phishing, credential harvesting, and session fixation.
- It can disrupt the OAuth/OIDC flow user experience by redirecting users to malicious domains disguised as legitimate pages (even though this path doesn't directly include tokens, it can be exploited for social engineering attacks through redirect chains).
- The impact can be amplified when redirect chains are combined with other vulnerabilities such as CSP bypass or cache poisoning.

## References
- https://github.com/lobehub/lobe-chat/security/advisories/GHSA-xph5-278p-26qx
- https://nvd.nist.gov/vuln/detail/CVE-2025-59426
- https://github.com/lobehub/lobe-chat/commit/70f52a3c1fadbd41a9db0e699d1e44d9965de445
- https://github.com/lobehub/lobe-chat
- https://github.com/lobehub/lobe-chat/blob/aa841a3879c30142720485182ad62aa0dbd74edc/src/app/(backend)/oidc/consent/route.ts#L113-L127
