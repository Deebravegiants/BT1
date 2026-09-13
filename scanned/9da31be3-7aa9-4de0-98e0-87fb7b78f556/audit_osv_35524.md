# [H] CVE-2026-10055

## Summary
Severity: High
Advisory: CVE-2026-10055
Aliases: GHSA-2m57-xxmh-v696
CVSS: 8.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/CVE-2026-10055
Type: osv

## Details
In Eclipse Theia since version 1.26.0, the backend /services/request-service RPC accepts an attacker-controlled URL from any client connected to the standard /services messaging endpoint, performs the HTTP request server-side, and returns the full response body to the caller.




Because the destination URL is neither validated nor allowlisted, a remote attacker with access to the Theia service connection can issue server-side HTTP requests to localhost or other backend-reachable hosts and read their responses, exposing internal administrative endpoints, cloud instance metadata services, and other resources that are intentionally outside the browser network boundary.




The vulnerability affects deployments where the Theia service connection is reachable by untrusted users (for example, multi-tenant or publicly-reachable Theia deployments).

## References
- https://gitlab.eclipse.org/security/vulnerability-reports/-/work_items/446
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10055.json
- https://github.com/eclipse-theia/theia/security/advisories/GHSA-2m57-xxmh-v696
- https://nvd.nist.gov/vuln/detail/CVE-2026-10055
