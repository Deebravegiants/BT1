# [H] Flowise affected by Server-Side Request Forgery (SSRF) in HTTP Node Leading to Internal Network Access

## Summary
Severity: High
Advisory: GHSA-fvcw-9w9r-pxc7
CVE: CVE-2026-31829
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-fvcw-9w9r-pxc7
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.0.13
- npm: `flowise-components` — affected >=0 <3.0.13

## Details
**Description:**
Flowise exposes an HTTP Node in AgentFlow and Chatflow that performs server-side HTTP requests using user-controlled URLs. By default, there are no restrictions on target hosts, including private/internal IP ranges (RFC 1918), localhost, or cloud metadata endpoints.
This enables Server-Side Request Forgery (SSRF), allowing any user interacting with a publicly exposed chatflow to force the Flowise server to make requests to internal network resources that are inaccessible from the public internet.

**Impact includes:**
- Access to internal admin panels (e.g., internal company dashboards, Jenkins, Kubernetes API, etc.).
- Retrieval of cloud provider metadata (e.g., AWS IMDSv1 at [http://169.254.169.254], GCP, Azure).
- Port scanning and enumeration of internal services.
- Potential lateral movement or privilege escalation in compromised environments.

This vulnerability is particularly severe because:
- Flowise instances are often deployed publicly without authentication (FLOWISE_USERNAME/PASSWORD not set by default).
- The HTTP Node is easily accessible in simple flows with minimal configuration.

**Proof of Concept (PoC):**
A minimal flow consisting of three nodes demonstrates successful internal network access:
Flow Structure:
<img width="1131" height="323" alt="image" src="https://github.com/user-attachments/assets/f6ddc74f-3ae9-4376-995a-693fb272627a" />
HTTP Node Configuration:
The HTTP Node is configured to perform a GET request to an internal address on localhost:
URL: http://127.0.0.1:8000 (or any internal service)
<img width="568" height="759" alt="image" src="https://github.com/user-attachments/assets/a5735e1f-f735-4d01-9d72-a772963254c8" />

Successful Response from Internal Service:
When the flow is triggered via chat input, the Flowise server successfully retrieves and returns content from the internal mock server running on port 8000 within the same container/network:
<img width="377" height="627" alt="image" src="https://github.com/user-attachments/assets/ff3fcfc6-4957-4aae-9c9d-13b4fca1d0ef" />


**Impact**
This is a Server-Side Request Forgery (SSRF) vulnerability with both read and write capabilities.
The HTTP Request node supports all standard HTTP methods (GET, POST, PUT, PATCH, DELETE), allowing attackers to not only retrieve sensitive information but also modify, create, or delete data on internal services if those services expose mutable endpoints:
- Read access: Retrieval of sensitive internal data, cloud provider metadata (e.g., AWS IAM credentials at http://169.254.169.254/latest/meta-data/iam/security-credentials/), secrets, configuration files, or database contents.
- Write access: Modification or deletion of internal resources via POST/PUT/PATCH/DELETE methods (e.g., creating malicious users/configurations, overwriting files, deleting data, triggering destructive actions on internal admin panels, CI/CD systems like Jenkins, Kubernetes APIs, or cloud management interfaces).
Amplification: Retrieved cloud credentials can be used for further privilege escalation or lateral movement outside the n8n instance.


Suggested Long-term Fix (for Flowise):
- Add optional security controls to HTTP Node:
- Toggle: "Block private IP ranges and localhost" (enabled by default).
- Field: "Allowed domains" (whitelist).
- Display prominent warning when URL field uses template variables (e.g., {{ }}).
- Update documentation with explicit SSRF risks and best practices.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-fvcw-9w9r-pxc7
- https://nvd.nist.gov/vuln/detail/CVE-2026-31829
- https://github.com/FlowiseAI/Flowise
