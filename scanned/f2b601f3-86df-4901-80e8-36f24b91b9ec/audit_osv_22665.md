# [H] Authenticated remote code execution due to insecure deserialization (GHSL-2022-063)

## Summary
Severity: High
Advisory: CVE-2022-36006
Aliases: GHSA-8867-q4xf-cqgm
CVSS: 7.9 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:L)
Published: 2022-08-14
Source: https://osv.dev/vulnerability/CVE-2022-36006
Type: osv

## Details
Arvados is an open source platform for managing, processing, and sharing genomic and other large scientific and biomedical data. A remote code execution (RCE) vulnerability in the Arvados Workbench allows authenticated attackers to execute arbitrary code via specially crafted JSON payloads. This exists in all versions up to 2.4.1 and is fixed in 2.4.2. This vulnerability is specific to the Ruby on Rails Workbench application (“Workbench 1”). We do not believe any other Arvados components, including the TypesScript browser-based Workbench application (“Workbench 2”) or API Server, are vulnerable to this attack. For versions of Arvados earlier than 2.4.2: remove the Ruby-based "Workbench 1" app ("apt-get remove arvados-workbench") from your installation as a workaround.

## References
- https://arvados.org/release-notes/2.4.2/
- https://dev.arvados.org/issues/19316
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/36xxx/CVE-2022-36006.json
- https://github.com/arvados/arvados/security/advisories/GHSA-8867-q4xf-cqgm
- https://nvd.nist.gov/vuln/detail/CVE-2022-36006
