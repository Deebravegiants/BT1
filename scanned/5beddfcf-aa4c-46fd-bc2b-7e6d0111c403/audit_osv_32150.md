# [C] Concorde not removing authentication tokens after logging out

## Summary
Severity: Critical
Advisory: CVE-2025-24973
Aliases: GHSA-2369-p2wh-7cc2
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-02-11
Source: https://osv.dev/vulnerability/CVE-2025-24973
Type: osv

## Details
Concorde, formerly know as Nexkey, is a fork of the federated microblogging platform Misskey. Prior to version 12.25Q1.1, due to an improper implementation of the logout process, authentication credentials remain in cookies even after a user has explicitly logged out, which may allow an attacker to steal authentication tokens. This could have devastating consequences if a user with admin privileges is (or was) using a shared device. Users who have logged in on a shared device should go to Settings > Security and regenerate their login tokens. Version 12.25Q1.1 fixes the issue. As a workaround, clear cookies and site data in the browser after logging out.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24973.json
- https://github.com/nexryai/concorde/security/advisories/GHSA-2369-p2wh-7cc2
- https://nvd.nist.gov/vuln/detail/CVE-2025-24973
- https://github.com/nexryai/concorde/commit/1f6ac9b289906083b132e4f9667a31a60ef83e4e
