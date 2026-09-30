# [C] n8n has Unauthenticated Expression Evaluation via Form Node

## Summary
Severity: Critical
Advisory: GHSA-75g8-rv7v-32f7
CVE: CVE-2026-27493
CWE: CWE-94, CWE-95
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-75g8-rv7v-32f7
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.22
- npm: `n8n` — affected >=2.0.0 <2.9.3
- npm: `n8n` — affected >=2.10.0 <2.10.1

## Details
## Impact
A second-order expression injection vulnerability existed in n8n's Form nodes that could allow an unauthenticated attacker to inject and evaluate arbitrary n8n expressions by submitting crafted form data. When chained with an expression sandbox escape, this could escalate to remote code execution on the n8n host.

The vulnerability requires a specific workflow configuration to be exploitable:
1. A form node with a field interpolating a value provided by an unauthenticated user, e.g. a form submitted value.
2. The field value must begin with an `=` character, which caused n8n to treat it as an expression and triggered a double-evaluation of the field content.
For example, a workflow uses a multi-step Form where a downstream Form node renders user-provided input back in an HTML field and precedes it with an `=` sign:
`=<h2>Thank you, {{ $input.first().json[\"Name\"] }}!</h2>`

There is no practical reason for a workflow designer to prefix a field with `=` intentionally — the character is not rendered in the output, so the result would not match the designer's expectations. If added accidentally, it would be noticeable and very unlikely to persist. An unauthenticated attacker would need to either know about this specific circumstance on a target instance or discover a matching form by chance.

Even when the preconditions are met, the expression injection alone is limited to data accessible within the n8n expression context. Escalation to remote code execution requires chaining with a separate sandbox escape vulnerability.

Due to these real-world constraints — the unlikely workflow configuration, the need for an additional sandbox escape, and the difficulty of discovery — we have assessed the severity as High rather than Critical, diverging from the base CVSS score to better reflect actual exploitability.

## Patches
The issue has been fixed in n8n versions 2.10.1, 2.9.3, and 1.123.22. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Review usage of form nodes manually for above mentioned preconditions.
- Disable the Form node by adding `n8n-nodes-base.form` to the `NODES_EXCLUDE` environment variable.
- Disable the Form Trigger node by adding `n8n-nodes-base.formTrigger` to the `NODES_EXCLUDE` environment variable.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-75g8-rv7v-32f7
- https://nvd.nist.gov/vuln/detail/CVE-2026-27493
- https://github.com/n8n-io/n8n/issues/19
- https://github.com/n8n-io/n8n/commit/562d867483e871b0f1e31776252e23bd721df75b
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@1.123.22
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.10.1
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.9.3
