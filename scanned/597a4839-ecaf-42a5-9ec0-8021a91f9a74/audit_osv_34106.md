# [M] Tuleap's special and always there fields permissions are not verified in cross-tracker search

## Summary
Severity: Medium
Advisory: CVE-2025-54877
Aliases: GHSA-m5qc-c3q5-2p29
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-08-29
Source: https://osv.dev/vulnerability/CVE-2025-54877
Type: osv

## Details
Tuleap is an Open Source Suite created to facilitate management of software development and collaboration. In Tuleap Community Edition versions before 16.10.99.1754050155 and Tuleap Enterprise Edition versions before 16.9-8 and before 16.10-5, an attacker can access to the content of the special and always there fields of accessible artifacts even if the permissions associated with the underlying fields do not allow it. This issue has been fixed in Tuleap Community Edition version 16.10.99.1754050155 and Tuleap Enterprise Edition versions 16.9-8 and 16.10-5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54877.json
- https://github.com/Enalean/tuleap/commit/b0c1328f96135ee6a3f84d0847be5f843eafa590
- https://github.com/Enalean/tuleap/security/advisories/GHSA-m5qc-c3q5-2p29
- https://nvd.nist.gov/vuln/detail/CVE-2025-54877
- https://tuleap.net/plugins/git/tuleap/tuleap/stable?a=commit&h=b0c1328f96135ee6a3f84d0847be5f843eafa590
- https://tuleap.net/plugins/tracker/?aid=44068
