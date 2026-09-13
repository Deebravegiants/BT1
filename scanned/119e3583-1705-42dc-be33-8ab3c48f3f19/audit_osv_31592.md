# [H] PostHog slack_incoming_webhook Server-Side Request Forgery Information Disclosure Vulnerability

## Summary
Severity: High
Advisory: CVE-2025-1521
CVSS: 7.1 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2025-04-23
Source: https://osv.dev/vulnerability/CVE-2025-1521
Type: osv

## Details
PostHog slack_incoming_webhook Server-Side Request Forgery Information Disclosure Vulnerability. This vulnerability allows remote attackers to disclose sensitive information on affected installations of PostHog. Authentication is required to exploit this vulnerability.

The specific flaw exists within the processing of the slack_incoming_webhook parameter. The issue results from the lack of proper validation of a URI prior to accessing resources. An attacker can leverage this vulnerability to execute code in the context of the service account. Was ZDI-CAN-25352.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/1xxx/CVE-2025-1521.json
- https://github.com/PostHog/posthog/commit/6e8f035f9acd339c5ba87ba6ea40fc1ab3053d42
- https://nvd.nist.gov/vuln/detail/CVE-2025-1521
- https://www.zerodayinitiative.com/advisories/ZDI-25-096/
