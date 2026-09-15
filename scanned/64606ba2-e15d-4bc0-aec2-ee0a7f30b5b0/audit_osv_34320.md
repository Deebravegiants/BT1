# [H] Apache Traffic Server: A simple legitimate POST request causes a crash

## Summary
Severity: High
Advisory: CVE-2025-58136
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2025-58136
Type: osv

## Details
A bug in POST request handling causes a crash under a certain condition.

This issue affects Apache Traffic Server: from 10.0.0 through 10.1.1, from 9.0.0 through 9.2.12.

Users are recommended to upgrade to version 10.1.2 or 9.2.13, which fix the issue.

A workaround for older versions is to set proxy.config.http.request_buffer_enabled to 0 (the default value is 0).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58136.json
- https://lists.apache.org/thread/2s11roxlv1j8ph6q52rqo1klvl01n14q
- https://nvd.nist.gov/vuln/detail/CVE-2025-58136
