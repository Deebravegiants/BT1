# [H] Aim allows denial of service due to no timeouts for some tracking server endpoints

## Summary
Severity: High
Advisory: GHSA-6w7p-xrvp-p7xv
CVE: CVE-2024-8061
CWE: CWE-1088, CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-6w7p-xrvp-p7xv
Type: github-advisory

## Affected
- PyPI: `aim` — affected >=0

## Details
In version 3.23.0 of aimhubio/aim, certain methods that request data from external servers do not have set timeouts, causing the server to wait indefinitely for a response. This can lead to a denial of service, as the tracking server does not respond to other requests while waiting. The issue arises in the client used by the `aim` tracking server to communicate with external resources, specifically in the `_run_read_instructions` method and similar calls without timeouts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8061
- https://github.com/aimhubio/aim
- https://github.com/aimhubio/aim/blob/a6c6f2fee0f1abe37c1d66701b0329fb6af31a3d/aim/ext/transport/client.py#L258
- https://huntr.com/bounties/c85d005c-b354-4c51-a88f-adda2f09622b
