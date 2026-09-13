# [M] RAGFlow < 0.26.3 - Server-Side Request Forgery via Agent Invoke Component

## Summary
Severity: Medium
Advisory: CVE-2026-75898
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:H/SI:L/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-75898
Type: osv

## Details
RAGFlow before 0.26.3 contains a server-side request forgery vulnerability in the agent workflow "Invoke" component (agent/component/invoke.py). The component builds an outbound request URL from canvas configuration and runtime template variables and passes it to requests.get, requests.post, or requests.put without calling the shared assert_url_is_safe validator or pinning the resolved address, unlike the crawler, SearXNG, file-upload, and RSS fetch paths. A user who can create or trigger an agent can direct the server to fetch loopback, link-local, and RFC 1918 destinations, including cloud instance metadata endpoints and services co-located on the deployment network, and the response body is returned as the component output. Where an agent is configured to interpolate the chat query into the Invoke URL, the destination is chosen by whoever can send that query.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75898.json
- https://github.com/infiniflow/ragflow/releases/tag/v0.26.3
- https://nvd.nist.gov/vuln/detail/CVE-2026-75898
- https://www.vulncheck.com/advisories/ragflow-server-side-request-forgery-via-agent-invoke-component
- https://github.com/infiniflow/ragflow/issues/15425
- https://github.com/infiniflow/ragflow/issues/18280
- https://github.com/infiniflow/ragflow/commit/c4fe68eaa0bf1d6442d2cd6ac2e35bc9ccbed34f
- https://github.com/infiniflow/ragflow/commit/e16d1a0150e1ca069beb538ae3dcd03f59edc5fa
- https://github.com/infiniflow/ragflow
- https://github.com/infiniflow/ragflow/blob/v0.26.2/agent/component/invoke.py#L168-L172
