# [H] Denial of service (DoS) via deformation `multipart/form-data` boundary

## Summary
Severity: High
Advisory: GHSA-59g5-xgcq-4qw3
CVE: CVE-2024-53981
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-12-02
Source: https://github.com/advisories/GHSA-59g5-xgcq-4qw3
Type: github-advisory

## Affected
- PyPI: `python-multipart` — affected >=0 <0.0.18

## Details
### Summary

When parsing form data, `python-multipart` skips line breaks (CR `\r` or LF `\n`) in front of the first boundary and any tailing bytes after the last boundary. This happens one byte at a time and emits a log event each time, which may cause excessive logging for certain inputs.

An attacker could abuse this by sending a malicious request with lots of data before the first or after the last boundary, causing high CPU load and stalling the processing thread for a significant amount of time. In case of ASGI application, this could stall the event loop and prevent other requests from being processed, resulting in a denial of service (DoS).

### Impact

Applications that use `python-multipart` to parse form data (or use frameworks that do so) are affected. 

### Original Report

This security issue was reported by:
- GitHub security advisory in Starlette on October 30 by @Startr4ck
- Email to `python-multipart` maintainer on October 3 by @mnqazi

## References
- https://github.com/Kludex/python-multipart/security/advisories/GHSA-59g5-xgcq-4qw3
- https://nvd.nist.gov/vuln/detail/CVE-2024-53981
- https://github.com/Kludex/python-multipart/commit/c4fe4d3cebc08c660e57dd709af1ffa7059b3177
- https://github.com/Kludex/python-multipart
