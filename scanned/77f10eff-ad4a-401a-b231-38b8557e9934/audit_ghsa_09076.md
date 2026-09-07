# [M] ninenines cowlib: Improper Neutralization of CRLF Sequences ('CRLF Injection') vulnerability allows SSE event splitting and injection via unvalidated field values

## Summary
Severity: Medium
Advisory: GHSA-hv23-4qp7-8c8r
CVE: CVE-2026-43968
CWE: CWE-93
Ecosystem: Hex
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-hv23-4qp7-8c8r
Type: github-advisory

## Affected
- Hex: `cowlib` — affected >=2.6.0 <2.16.1

## Details
Improper Neutralization of CRLF Sequences ('CRLF Injection') vulnerability in ninenines cowlib allows SSE event splitting and injection via unvalidated field values.

cow_sse:event/1 in cowlib guards the id and event fields against \n but not against bare \r, and the internal prefix_lines/2 function used for data and comment fields splits only on \n. Because the SSE specification requires decoders to treat \r\n, \r, and \n as equivalent line terminators, an attacker who controls any of these fields can inject additional SSE lines and forge a complete event with an arbitrary event type and data payload on the receiving end. In typical deployments where browser EventSource clients or other SSE consumers dispatch on event.type and render event.data, this enables event splitting, client-side logic manipulation, and stored-XSS-equivalent behaviour when event data is inserted into the DOM.

This issue affects cowlib from 2.6.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-43968
- https://github.com/ninenines/cowlib/commit/6165fc40efa159ba1cceee7e7981e790acba5d9c
- https://cna.erlef.org/cves/CVE-2026-43968.html
- https://github.com/ninenines/cowlib
- https://github.com/ninenines/cowlib/releases/tag/2.16.1
- https://osv.dev/vulnerability/EEF-CVE-2026-43968
