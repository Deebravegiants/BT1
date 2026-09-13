# [H] hashi-vault-js has a path traversal and query parameter injection

## Summary
Severity: High
Advisory: GHSA-g956-2f74-rmv7
CVE: CVE-2026-55100
CWE: CWE-23, CWE-74
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-g956-2f74-rmv7
Type: github-advisory

## Affected
- npm: `hashi-vault-js` — affected >=0 <0.5.2

## Details
## Summary

The `hashi-vault-js` library is vulnerable to path traversal and query string injection due to the lack of proper encoding of identifiers in path segments and query strings. This allows attackers to manipulate the request URL and potentially access unintended downstream endpoints or inject malicious parameters if untrusted input is passed to the library.

## Details

There are zero calls to `encodeURIComponent` anywhere in `Vault.js`. Every identifier (e.g., name, username, group, role, version) provided to the library is concatenated straight into the HTTP URL without URI encoding.

Two vectors can be dynamically confirmed:

1. **Path Traversal:** Passing `../../sys/seal` as a secret name causes the HTTP client to normalize the path and send the request to `/v1/sys/seal` instead of the intended Key-Value path.
2. **Query Injection:** Passing `1&list=true` as a version value injects an extra query parameter into the request payload.

## Impact

In applications where Vault identifiers originate from untrusted user input, this allows an unauthenticated attacker to redirect requests to unintended Vault endpoints (including administrative paths under `sys/`) or otherwise alter the executed query, executing operations within the permissions of the Vault token used by the application.

## Patches

This vulnerability has been addressed by wrapping path segments with `encodeURIComponent()` and safely formatting query strings instead of manual string concatenation. Users should upgrade to a version that includes this fix.

## Workarounds

If you cannot immediately update the library, you can mitigate this issue by rigidly validating and sanitizing all user-supplied input before passing it into `hashi-vault-js` methods. Alternatively, manually encode inputs using `encodeURIComponent()` before supply them to the library's functions.

## Acknowledgements

hashi-vault-js would like to thank Sebastián Alba Vives for reporting this vulnerability.

## References
- https://github.com/kyndryl-open-source/hashi-vault-js/security/advisories/GHSA-g956-2f74-rmv7
- https://github.com/kyndryl-open-source/hashi-vault-js/pull/66
- https://github.com/kyndryl-open-source/hashi-vault-js/commit/ea2f76052d366a08f35f62ef4c12b6a334c91ec2
- https://github.com/kyndryl-open-source/hashi-vault-js
- https://github.com/kyndryl-open-source/hashi-vault-js/releases/tag/v0.5.2
