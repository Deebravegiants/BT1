# [C] Remote Code Execution in Databasir

## Summary
Severity: Critical
Advisory: CVE-2022-24861
Aliases: GHSA-5r2v-wcwh-7xmp
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-04-20
Source: https://osv.dev/vulnerability/CVE-2022-24861
Type: osv

## Details
Databasir is a team-oriented relational database model document management platform. Databasir 1.01 has remote code execution vulnerability. JDBC drivers are not validated prior to use and may be provided by users of the system. This can lead to code execution by any basic user who has access to the system. Users are advised to upgrade. There are no known workarounds to this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24861.json
- https://github.com/vran-dev/databasir/security/advisories/GHSA-5r2v-wcwh-7xmp
- https://nvd.nist.gov/vuln/detail/CVE-2022-24861
- https://github.com/vran-dev/databasir/commit/ca22a8fef7a31c0235b0b2951260a7819b89993b
- https://github.com/vran-dev/databasir/pull/103
