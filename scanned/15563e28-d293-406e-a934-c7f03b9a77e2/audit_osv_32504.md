# [H] Zulip Authentication Backend Configuration Bypass

## Summary
Severity: High
Advisory: CVE-2025-31478
Aliases: GHSA-qxfv-j6vg-5rqc
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-31478
Type: osv

## Details
Zulip is an open-source team collaboration tool. Zulip supports a configuration where account creation is limited solely by being able to authenticate with a single-sign on authentication backend, meaning the organization places no restrictions on email address domains or invitations being required to join, but has disabled the EmailAuthBackend that is used for email/password authentication. A bug in the Zulip server means that it is possible to create an account in such organizations, without having an account with the configured SSO authentication backend. This issue is patched in version 10.2. A workaround includes requiring invitations to join the organization prevents the vulnerability from being accessed.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/31xxx/CVE-2025-31478.json
- https://github.com/zulip/zulip/security/advisories/GHSA-qxfv-j6vg-5rqc
- https://nvd.nist.gov/vuln/detail/CVE-2025-31478
- https://github.com/zulip/zulip/commit/b5ab90aaa4a7efdcbf886cb9e7d55fa5bfca3a28
