# [H] Insecure Jinja2 templates rendered in Haystack Components can lead to RCE

## Summary
Severity: High
Advisory: GHSA-hx9v-6r9f-w677
CVE: CVE-2024-41950
CWE: CWE-1336
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-31
Source: https://github.com/advisories/GHSA-hx9v-6r9f-w677
Type: github-advisory

## Affected
- PyPI: `haystack-ai` — affected >=0 <2.3.1

## Details
### Impact

Haystack clients that let their users create and run Pipelines from scratch are vulnerable to remote code executions.

Certain Components in Haystack use Jinja2 templates, if anyone can create and render that template on the client machine they run any code.

### Patches

The problem has been fixed with PRs deepset-ai/haystack#8095 and deepset-ai/haystack#8096.

Both have been released with Haystack `2.3.1`.

### Workarounds

Prevent users from running the affected Components, or only let users use preselected templates.

### References

The list of impacted Components can be found in the release notes for `2.3.1`.
https://github.com/deepset-ai/haystack/releases/tag/v2.3.1

## References
- https://github.com/deepset-ai/haystack/security/advisories/GHSA-hx9v-6r9f-w677
- https://nvd.nist.gov/vuln/detail/CVE-2024-41950
- https://github.com/deepset-ai/haystack/pull/8095
- https://github.com/deepset-ai/haystack/pull/8096
- https://github.com/deepset-ai/haystack/commit/3fed1366c448b02189851bf08166c1f6477a02b0
- https://github.com/deepset-ai/haystack/commit/6c25a5c73e83aa32c3241ba84a5cbb3ac0e8a89e
- https://github.com/deepset-ai/haystack
- https://github.com/deepset-ai/haystack/releases/tag/v2.3.1
