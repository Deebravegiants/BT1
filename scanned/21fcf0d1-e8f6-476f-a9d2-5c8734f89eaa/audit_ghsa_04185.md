# [M] LangGraph SDK has unsafe URL path construction

## Summary
Severity: Medium
Advisory: GHSA-w39p-vh2g-g8g5
CVE: CVE-2026-48776
CWE: CWE-22, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-w39p-vh2g-g8g5
Type: github-advisory

## Affected
- PyPI: `langgraph-sdk` — affected >=0 <0.3.15

## Details
## Summary

`langgraph-sdk` constructs HTTP request paths for resource operations by interpolating caller-supplied identifier values into URL templates. Without sanitization of those values, identifiers that contain characters with special meaning in URL paths could cause the resulting request to address a different resource (and potentially a different resource type) than the SDK method's call site indicates. In deployments where the SDK receives identifier values that originate from untrusted sources, this could result in unintended access, modification, or deletion of resources beyond the calling user's authorization scope.

This issue is most consequential in deployments that:

- forward end-user-supplied values directly into SDK identifier parameters without first validating them against an expected format (such as a UUID), and
- rely on URL-prefix-based authorization at an upstream layer (reverse proxy, edge gateway, WAF), where the authorization decision is made on the SDK call's intended path rather than on the final delivered request path.

There have no evidence of this behavior being triggered in the wild. This change is intended to reduce the surface available when caller-supplied identifier values originate from untrusted sources.

## Affected users / systems

You may be affected if you:

- use `langgraph-sdk` (Python) to address resources by identifier, and
- pass identifier values into SDK methods that originate from end-user input, untrusted third-party callers, or any source that does not validate identifier format before the SDK call.

Applications that validate identifier values (for example, by parsing them as UUIDs and rejecting anything that does not parse) before passing them to SDK methods are not affected. Validated UUIDs round-trip through the SDK request path unchanged.

## Impact

- Potential **unintended access, modification, or deletion** of resources via SDK methods called for a different resource type, when caller-supplied identifier values are not validated.
- In deployments with prefix-based authorization at an upstream layer, the authorization decision and the final delivered request path may diverge.
- Confidentiality: disclosure of resource content beyond the authorization scope of the calling user.
- Integrity: modification or deletion of resources beyond the authorization scope of the calling user.

## Patches / mitigation

The SDK now applies path-segment encoding to identifier values before they are interpolated into request URL templates. After this change, identifier values that contain characters with special meaning in URL paths are transmitted as encoded byte sequences and routed to the resource the SDK method's call site indicates.

## Compatibility

Identifier values that match the standard UUID format, or any other format that contains only characters safe to transmit unencoded in URL path segments, round-trip through the SDK request path unchanged. Applications that already validate identifier inputs see no behavioral change.

## Operational guidance

- Validate identifier values (typically as UUIDs) at the boundary where untrusted input enters the application, before passing them to SDK methods.
- For deployments relying on URL-prefix-based authorization upstream of LangGraph, prefer authorization at the LangGraph server layer or on parsed-and-validated request paths rather than on raw URL prefixes.

## LangSmith / hosted deployments note

This issue affects the SDK that runs in caller applications. The LangGraph server runtime, including LangSmith-hosted deployments, receives ordinary HTTP requests on documented routes and is not itself affected by this issue. Applications that consume LangSmith-hosted services via `langgraph-sdk` and pass untrusted identifier values to SDK methods should upgrade.

First reported by: pucagit (CyStack).

## References
- https://github.com/langchain-ai/langgraph/security/advisories/GHSA-w39p-vh2g-g8g5
- https://nvd.nist.gov/vuln/detail/CVE-2026-48776
- https://github.com/advisories/GHSA-w39p-vh2g-g8g5
- https://github.com/langchain-ai/langgraph
- https://github.com/langchain-ai/langgraph/releases/tag/sdk%3D%3D0.3.15
- https://github.com/pypa/advisory-database/tree/main/vulns/langgraph-sdk/PYSEC-2026-2575.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/langgraph/PYSEC-2026-2194.yaml
- https://pypi.org/project/langgraph-sdk
