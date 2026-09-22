# [H] LangSmith SDK TracingMiddleware: Arbitrary server-side file read

## Summary
Severity: High
Advisory: GHSA-f4xh-w4cj-qxq8
CWE: CWE-22, CWE-346, CWE-843
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-f4xh-w4cj-qxq8
Type: github-advisory

## Affected
- PyPI: `langsmith` — affected >=0 <0.8.18

## Details
# Summary

An attacker who can send an HTTP request to a server running the LangSmith SDK's `TracingMiddleware` can cause that server to read an arbitrary file from its local filesystem and upload the contents to LangSmith as a trace attachment. Depending on how the distributed trace system is deployed, triggering a read may not require authentication. Retrieving the contents requires read access to the LangSmith workspace the traces are sent to. The net effect is a trust-boundary crossing: a party with workspace trace-read access (for example a low-privilege workspace member, a contractor, or a compromised teammate account) gains the ability to read files from any server running `TracingMiddleware`, a capability outside that workspace's intended trust boundary.

# Impact

Confidentiality (High): arbitrary read of files accessible to the server process, exposed to anyone with workspace trace-read access.

# Details

Two defects combine. A field supplied through a tracing-propagation header was merged into the run without validation, allowing injection of run attributes including attachments (CWE-346). A type check intended to gate filesystem access did not match the type of the decoded input, so the guard never engaged (CWE-843). As a result, an attacker-named file is opened by the server and uploaded as a trace attachment by the background tracing thread (CWE-22).

## Who can exploit this

- Anyone reachable by HTTP can trigger the file read. Depending on how the distributed trace system is deployed, triggering may not require authentication.
- Retrieving the file contents requires read access to the destination LangSmith workspace. The upload uses the server's own configured API key and workspace, which the attacker cannot redirect, so a zero-access outsider cannot retrieve the result; a workspace member, or anyone who has compromised one, can.

# Remediation

Upgrade the Python SDK to `>= 0.8.18`.

# Workarounds

Until upgrading, do not expose `TracingMiddleware` to untrusted HTTP traffic, and limit workspace trace-read access to trusted members.

# Credits

First reported by @Ryu7zz.

## References
- https://github.com/langchain-ai/langsmith-sdk/security/advisories/GHSA-f4xh-w4cj-qxq8
- https://github.com/langchain-ai/langsmith-sdk
