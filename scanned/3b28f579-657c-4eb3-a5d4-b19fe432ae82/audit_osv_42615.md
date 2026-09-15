# [H] Apache CloudStack: SAML2 Signature Validation Silently Skipped for Cert-less IdP

## Summary
Severity: High
Advisory: CVE-2026-68745
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-68745
Type: osv

## Details
Certificate validation failures in SAML authentication in Apache CloudStack 4.20.3.0 and 4.22.1.0 on all platforms allow a malicious agent to forge a SAML response to the management server. The agent will have to spoof the ip address of the IdP or get an url of its own choosing registered in the management server, after which it can allow logging on with forged signatures.

Users are recommended to upgrade to versions 4.20.3.1 or 4.22.1.1 and above, which fix this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68745.json
- https://lists.apache.org/thread/g6cwddtjrwbh1d56wjz4cfp3fzfm4kbc
- https://nvd.nist.gov/vuln/detail/CVE-2026-68745
