# [M] Anki: User scripts in iframes have access to the internal Anki API

## Summary
Severity: Medium
Advisory: GHSA-cw6h-ffmh-x6vh
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-cw6h-ffmh-x6vh
Type: github-advisory

## Affected
- PyPI: `aqt` — affected >=0 <25.9.4

## Details
## Summary

Anki's webview-based pages communicate with the Rust backend using an internal localhost API. Anki implements measures to prevent user scripts run in the reviewer/editor from accessing this API (https://github.com/ankitects/anki/pull/3925) but it inadvertently allows access to scripts included via iframes in the editor. While overall only a limited set of API methods are exposed, some such as `getImageForOcclusion` can read arbitrary files.

**CWE:** CWE-22 (Path Traversal)
**Reporter:** Bankde (Eakasit)

## Affected Products

| Ecosystem | Package | Affected Versions |
| --------- | ------- | ----------------- |
| PyPI      | `aqt`   | `<= 25.09.3`      |

## Impact

Any desktop Anki user (Windows, macOS, Linux) who imports an untrusted `.apkg` and views card with an embedded iframe is vulnerable. No special configuration is required. The attacker can read any file accessible to the Anki process and exfiltrate its contents over the network.

## Patches

A patch is available in 25.09.4

## Workarounds

- Do not import `.apkg` files from untrusted sources.
- Inspect `.apkg` contents (it's a ZIP) for `.html`/`.svg` files with `<script>` tags before importing.
- Block unexpected outbound network requests from the Anki process at the firewall level.

## References

- Vulnerability report: _Anki arbitrary file read vulnerability (with exfiltration)_ — Bankde (Eakasit)
- Affected source: [`qt/aqt/mediasrv.py::_handle_local_file_request`](https://github.com/ankitects/anki/blob/5a9b54e9380c66e26391f0827867d2a728107836/qt/aqt/mediasrv.py#L223)
- Related prior CVEs: [CVE-2024-29073](https://nvd.nist.gov/vuln/detail/CVE-2024-29073), [CVE-2024-32484](https://nvd.nist.gov/vuln/detail/CVE-2024-32484), [CVE-2025-62185](https://nvd.nist.gov/vuln/detail/CVE-2025-62185), [CVE-2025-62187](https://nvd.nist.gov/vuln/detail/CVE-2025-62187)

## References
- https://github.com/ankitects/anki/security/advisories/GHSA-cw6h-ffmh-x6vh
- https://github.com/ankitects/anki
