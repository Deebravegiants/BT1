# [H] Apache NimBLE: Incorrect data validation in BASS add/modify source operation

## Summary
Severity: High
Advisory: CVE-2026-45813
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-45813
Type: osv

## Details
Out-of-bounds Write, Integer Underflow (Wrap or Wraparound) vulnerability in Apache NimBLE BASS service.
Improper validation when parsing BASS service  "Add Source" and "Modify Source" operation PDU could results in stack buffer overflow or arbitrary out-of-bound read.


This can be triggered by nearby devices over Bluetooth connection, however pairing is required prior to accessing BASS service, which depending on device configuration may or may not require user action.

This issue affects Apache NimBLE: through 1.9.0.

Users are recommended to upgrade to version 1.10.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/24/13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45813.json
- https://lists.apache.org/thread/vc1ny73w243z5wr6t0y10gc6t2c9cytw
- https://nvd.nist.gov/vuln/detail/CVE-2026-45813
- https://github.com/apache/mynewt-nimble/pull/2232
