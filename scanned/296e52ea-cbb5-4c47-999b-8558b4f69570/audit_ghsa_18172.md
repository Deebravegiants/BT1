# [C] InvokeAI has External Control of File Name or Path

## Summary
Severity: Critical
Advisory: GHSA-vv9c-xxg7-wmv7
CVE: CVE-2025-6237
CWE: CWE-22, CWE-73
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-09-18
Source: https://github.com/advisories/GHSA-vv9c-xxg7-wmv7
Type: github-advisory

## Affected
- PyPI: `invokeai` — affected >=0 <6.7.0

## Details
### Path Traversal Vulnerability in InvokeAI

A path traversal vulnerability in **InvokeAI** (versions < 6.7.0) allows an unauthenticated remote attacker to read files outside the intended media directory via the **bulk downloads** API.

The endpoint accepts a user-controlled file/item name and concatenates it into a filesystem path without proper canonicalization or allow-listing. By supplying sequences such as `../` (or absolute paths), an attacker can cause the server to traverse directories and return arbitrary files.

In certain storage or back-end configurations, abusing attacker-controlled paths can also lead to unintended overwriting or deletion of files referenced by the crafted path.

The issue is fixed in **6.7.0**, which normalizes and validates input paths and rejects traversal attempts.

**Affected versions:** `< 6.7.0`
**Patched version:** `6.7.0`

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-6237
- https://github.com/invoke-ai/InvokeAI/pull/8548/commits/eff565ae6ace1c8458f187245690bff0513f1b9e
- https://github.com/invoke-ai/InvokeAI
- https://github.com/invoke-ai/InvokeAI/blob/v6.0.0a1/invokeai/app/api/routers/images.py#L493-L524
- https://github.com/invoke-ai/InvokeAI/releases/tag/v6.7.0
- https://huntr.com/bounties/54ac9589-7c88-4fd4-8512-8b2f19fbaedf
