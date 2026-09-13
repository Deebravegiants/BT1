# [H] Broken Access Control in Opal filesystem's copy functionality exposes all user data

## Summary
Severity: High
Advisory: CVE-2025-27101
Aliases: GHSA-rxmx-gqjj-vhv8
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2025-03-11
Source: https://osv.dev/vulnerability/CVE-2025-27101
Type: osv

## Details
Opal is OBiBa’s core database application for biobanks or epidemiological studies. Prior to version 5.1.1, when copying any parent directory to a folder in the /temp/ directory, all files in that parent directory are copied, including files which the user should not have access to. All users of the application are impacted, as this is exploitable by any user to reveal all files in the opal filesystem. This also means that low-privilege users such as DataShield users can retrieve the files of other users. Version 5.1.1 contains a patch for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27101.json
- https://github.com/obiba/opal/security/advisories/GHSA-rxmx-gqjj-vhv8
- https://nvd.nist.gov/vuln/detail/CVE-2025-27101
- https://github.com/obiba/opal/commit/fca7dc9c8348064741b2e8b2c31b66660a935743
