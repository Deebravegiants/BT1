# [H] Improper Handling of Insufficient Permissions or Privileges  in Conduit

## Summary
Severity: High
Advisory: CVE-2024-6302
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-06-25
Source: https://osv.dev/vulnerability/CVE-2024-6302
Type: osv

## Details
Lack of privilege checking when processing a redaction in Conduit versions v0.6.0 and lower, allowing a local user to redact any message from users on the same server, given that they are able to send redaction events.

## References
- https://conduit.rs/changelog/#v0-7-0-2024-04-25
- https://gitlab.com/famedly/conduit/-/releases/v0.7.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6302.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-6302
