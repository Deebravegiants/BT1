# [M] NocoDB has Blind SSRF via Unvalidated HEAD Request in uploadViaURL Functionality

## Summary
Severity: Medium
Advisory: GHSA-xr7v-j379-34v9
CVE: CVE-2026-24767
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-01-28
Source: https://github.com/advisories/GHSA-xr7v-j379-34v9
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0 <0.301.0

## Details
## Summary

A **blind Server-Side Request Forgery (SSRF)** vulnerability exists in the `uploadViaURL` functionality due to an unprotected `HEAD` request. While the subsequent file retrieval logic correctly enforces SSRF protections, the initial metadata request executes without validation.

This allows limited outbound requests to arbitrary URLs before SSRF controls are applied.

---

## Vulnerability Details

The `uploadViaURL()` function issues an `axios.head()` request to retrieve metadata (content type, content length, and final URL after redirects). This request is performed **without SSRF filtering**.

Although the actual file download is protected by request filtering, the initial `HEAD` request occurs prior to these checks and can be triggered with an attacker-controlled URL.

### Vulnerable Code

```ts
if (!url.startsWith('data:')) {
  response = await axios.head(url, { maxRedirects: 5 });
  mimeType = response.headers['content-type']?.split(';')[0];
  size = response.headers['content-length'];
  finalUrl = response.request.res.responseUrl;
}
```

---

## Impact

The impact of this issue is **limited** due to the following constraints:

* Only `HEAD` requests are affected (no response body is returned)
* No direct exfiltration of response data occurs
* The subsequent file-fetching logic enforces SSRF protections

However, the vulnerability may still allow:

* **Blind SSRF** via outbound `HEAD` requests
* **Limited internal service probing** (reachability and response behavior)
* **Interaction with sensitive internal endpoints** that respond to `HEAD` requests

This issue does **not** provide arbitrary data access or full internal network compromise on its own.

---

## Severity

**Moderate**

The vulnerability is limited in scope and impact:

* Only `HEAD` requests are affected
* No response body or sensitive data is directly returned
* The actual file download logic enforces SSRF protections

While the issue permits blind outbound requests to attacker-controlled URLs, it does not enable direct data exfiltration or full internal network compromise on its own.

---

## Proof of Concept

```bash
curl -X POST 'http://localhost:8080/api/v2/storage/upload-by-url' \
  -H 'Content-Type: application/json' \
  -H 'xc-auth: <token>' \
  -d '[{
    "url": "http://169.254.169.254/latest/meta-data/",
    "fileName": "test.txt"
  }]'
```

This request causes the server to issue an unfiltered `HEAD` request before SSRF protections are applied.

---

## Acknowledgements

This issue was first identified and responsibly disclosed by Faizan Raza of Kolega.dev as part of a security assessment using Kolega.dev Deep Code Scan, including validation and fix recommendations.

NocoDB also acknowledges Neel B for independently reporting the same issue prior to publication.

NocoDB thanks Kolega.dev for their contribution to improving the security posture of the project.

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-xr7v-j379-34v9
- https://nvd.nist.gov/vuln/detail/CVE-2026-24767
- https://github.com/nocodb/nocodb
