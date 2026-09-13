# [H] Apache NimBLE: Buffer overflow in socket HCI transport

## Summary
Severity: High
Advisory: CVE-2026-45811
CVSS: 7.5 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-45811
Type: osv

## Details
Buffer Copy without Checking Size of Input ('Classic Buffer Overflow') vulnerability in Apache NimBLE.
The HCI socket transport did not check whether a received HCI event would fit the configured event pool before copying it, allowing a buffer overflow. Severity is low: exploitation requires either a misconfigured pool size or a malicious/compromised controller on the other end of the HCI socket link, not over-the-air Bluetooth access.

This issue affects Apache NimBLE: through 1.9.0.

Users are recommended to upgrade to version 1.10.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/24/11
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45811.json
- https://lists.apache.org/thread/5mkz68y1py0o6zmxtc3l1o8grtrb78m0
- https://nvd.nist.gov/vuln/detail/CVE-2026-45811
- https://github.com/apache/mynewt-nimble/commit/dcc4e4f026109eecd507de9479bb5019306a4a41
