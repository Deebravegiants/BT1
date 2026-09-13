# [C] globalpom-utils has Insecure Temporary File

## Summary
Severity: Critical
Advisory: GHSA-jjvp-wfp8-rv69
CVE: CVE-2018-25068
CWE: CWE-377, CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-06
Source: https://github.com/advisories/GHSA-jjvp-wfp8-rv69
Type: github-advisory

## Affected
- Maven: `com.anrisoftware.globalpom:globalpomutils` — affected >=0 <4.5.1

## Details
A vulnerability has been found in devent globalpom-utils up to 4.5.0 and classified as critical. This vulnerability affects the function `createTmpDir` of the file `globalpomutils-fileresources/src/main/java/com/anrisoftware/globalpom/fileresourcemanager/FileResourceManagerProvider.java`. The manipulation leads to insecure temporary file. The attack can be initiated remotely. Upgrading to version 4.5.1 can address this issue. The name of the patch is 77a820bac2f68e662ce261ecb050c643bd7ee560. It is recommended to upgrade the affected component. VDB-217570 is the identifier assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-25068
- https://github.com/devent/globalpom-utils/commit/77a820bac2f68e662ce261ecb050c643bd7ee560
- https://github.com/devent/globalpom-utils
- https://github.com/devent/globalpom-utils/releases/tag/globalpomutils-4.5.1
- https://vuldb.com/?ctiid.217570
- https://vuldb.com/?id.217570
