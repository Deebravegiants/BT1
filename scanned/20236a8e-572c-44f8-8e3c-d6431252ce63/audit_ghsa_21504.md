# [H] ManyDesigns Portofino subject to creation of insecure temporary file

## Summary
Severity: High
Advisory: GHSA-925r-r6rp-2jj7
CVE: CVE-2022-3952
CWE: CWE-377, CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-11-11
Source: https://github.com/advisories/GHSA-925r-r6rp-2jj7
Type: github-advisory

## Affected
- Maven: `com.manydesigns:portofino` — affected >=0 <5.3.3

## Details
A vulnerability has been found in ManyDesigns Portofino 5.3.2. Affected by this vulnerability is the function createTempDir of the file WarFileLauncher.java. The manipulation leads to creation of temporary file in directory with insecure permissions. Upgrading to version 5.3.3 is able to address this issue. The name of the patch is 94653cb357806c9cf24d8d294e6afea33f8f0775. It is recommended to upgrade the affected component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3952
- https://github.com/ManyDesigns/Portofino/pull/580
- https://github.com/ManyDesigns/Portofino/commit/94653cb357806c9cf24d8d294e6afea33f8f0775
- https://github.com/ManyDesigns/Portofino
- https://github.com/ManyDesigns/Portofino/releases/tag/v5.3.3
- https://vuldb.com/?id.213457
