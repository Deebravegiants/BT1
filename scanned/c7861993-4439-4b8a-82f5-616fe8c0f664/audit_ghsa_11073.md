# [H] Envoy has RBAC Header Validation Bypass via Multi-Value Header Concatenation

## Summary
Severity: High
Advisory: GHSA-ghc4-35x6-crw5
CVE: CVE-2026-26308
CWE: CWE-20, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-ghc4-35x6-crw5
Type: github-advisory

## Affected
- Go: `github.com/envoyproxy/envoy` — affected >=1.37.0 <1.37.1
- Go: `github.com/envoyproxy/envoy` — affected >=1.36.0 <1.36.5
- Go: `github.com/envoyproxy/envoy` — affected >=1.35.0 <1.35.9
- Go: `github.com/envoyproxy/envoy` — affected >=0 <1.34.13

## Details
## 1. Summary
The Envoy RBAC (Role-Based Access Control) filter contains a logic vulnerability in how it validates HTTP headers when multiple values are present for the same header name. Instead of validating each header value individually, Envoy concatenates all values into a single comma-separated string. This behavior allows attackers to bypass RBAC policies—specifically "Deny" rules—by sending duplicate headers, effectively obscuring the malicious value from exact-match mechanisms.

## 2. Attack Scenario
Consider an environment where an administrator wants to block external access to internal resources using a specific header flag.

### Configuration
The Envoy proxy is configured with a **Deny** rule to reject requests containing the header `internal: true`.
* **Rule Type:** Exact Match
* **Target:** `internal` header must not equal `true`.

### The Bypass Logic
1.  **Standard Request (Blocked):**
    * **Input:** `internal: true`
    * **Envoy Processing:** Sees string `"true"`.
    * **Result:** Match found. **Request Denied.**

2.  **Exploit Request (Bypassed):**
    * **Input:**
        ```http
        internal: true
        internal: true
        ```
    * **Envoy Processing:** Concatenates values into `"true,true"`.
    * **Matcher Evaluation:** Does `"true,true"` equal `"true"`? **No.**
    * **Result:** The Deny rule fails to trigger. **Request Allowed.**

## 3. Implications
* **RBAC Bypass:** Remote attackers can bypass configured access controls.
* **Unauthorized Access:** Sensitive internal resources or administrative endpoints protected by header-based Deny rules become accessible.
* **Risk:** High, particularly for deployments relying on "Exact Match" strategies for security blocking.

## 4. Reproduction Steps
To verify this vulnerability:

1.  **Deploy Envoy:** Configure an instance with an RBAC **Deny** rule that performs an **exact match** on a specific header (e.g., `internal: true`).
2.  **Baseline Test:** Send a request containing the header `internal: true`.
    * *Observation:* Envoy blocks this request (HTTP 403).
3.  **Exploit Test:** Send a second request containing the same header twice:
    ```http
    GET /restricted-resource HTTP/1.1
    Host: example.com
    internal: true
    internal: true
    ```
    * *Observation:* Envoy allows the request, granting access to the resource.

## 6. Recommendations
**Fix Header Validation Logic:**
Modify the RBAC filter to validate each header value instance individually. Avoid relying on the concatenated string output of `getAllOfHeaderAsString()` for security-critical matching unless the matcher is explicitly designed to parse comma-separated lists.

** Examine the DENY role to use a Regex style fix.

**Credit:** Dor Konis

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-ghc4-35x6-crw5
- https://nvd.nist.gov/vuln/detail/CVE-2026-26308
- https://github.com/envoyproxy/envoy/commit/b6ba0b2294b98484fb0ed8556897d1073cc27867
- https://github.com/envoyproxy/envoy
