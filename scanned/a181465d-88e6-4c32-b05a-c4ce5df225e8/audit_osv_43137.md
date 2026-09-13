# [H] OpenSignLabs OpenSign - Insufficient Verification of Data Authenticity

## Summary
Severity: High
Advisory: CVE-2026-72544
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-72544
Type: osv

## Details
An integrity verification vulnerability in OpenSignLabs OpenSign through 2.37.0 allows unauthenticated remote attackers to forge document audit-trail entries via the triggerevent Parse cloud function. The function accepts viewer identity and IP address as caller-supplied parameters without authentication, allowing fabrication of arbitrary audit log entries. An attacker can tamper with the legal audit trail of any signed document, undermining non-repudiation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72544.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72544
- https://github.com/OpenSignLabs/OpenSign
