# [H] AutomataCI Release Job Can Revert Repo to First Commit

## Summary
Severity: High
Advisory: CVE-2023-42798
Aliases: GHSA-6q23-vhhg-8h89
CVSS: 8.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:N/I:H/A:H)
Published: 2023-09-22
Source: https://osv.dev/vulnerability/CVE-2023-42798
Type: osv

## Details
AutomataCI is a template git repository equipped with a native built-in semi-autonomous CI tools. An issue in versions 1.4.1 and below can let a release job reset the git root repository to the first commit. Version 1.5.0 has a patch for this issue. As a workaround, make sure the `PROJECT_PATH_RELEASE` (e.g. `releases/`) directory is manually and actually `git cloned` properly, making it a different git repostiory from the root git repository.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/42xxx/CVE-2023-42798.json
- https://github.com/ChewKeanHo/AutomataCI/security/advisories/GHSA-6q23-vhhg-8h89
- https://nvd.nist.gov/vuln/detail/CVE-2023-42798
- https://github.com/ChewKeanHo/AutomataCI/issues/93
