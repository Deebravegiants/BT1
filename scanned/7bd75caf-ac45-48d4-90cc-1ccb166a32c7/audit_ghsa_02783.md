# [C] Deserialization of Untrusted Data in org.apache.ddlutils:ddlutils

## Summary
Severity: Critical
Advisory: GHSA-9378-f4v7-jgm4
CVE: CVE-2021-41616
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-04
Source: https://github.com/advisories/GHSA-9378-f4v7-jgm4
Type: github-advisory

## Affected
- Maven: `org.apache.ddlutils:ddlutils` — affected >=0

## Details
Apache DB DdlUtils 1.0 included a BinaryObjectsHelper that was intended for use when migrating database data with a SQL data type of BINARY, VARBINARY, LONGVARBINARY, or BLOB between databases using the ddlutils features. The BinaryObjectsHelper class was insecure and used ObjectInputStream.readObject without validating that the input data was safe to deserialize. Please note that DdlUtils is no longer being actively developed. To address the insecurity of the BinaryObjectHelper class, the following changes to DdlUtils have been made: (1) BinaryObjectsHelper.java has been deleted from the DdlUtils source repository and the DdlUtils feature of propagating data of SQL binary types is therefore no longer present in DdlUtils; (2) The ddlutils-1.0 release has been removed from the Apache Release Distribution Infrastructure; (3) The DdlUtils web site has been updated to indicate that DdlUtils is now available only as source code, not as a packaged release.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41616
- https://github.com/apache/ddlutils
- https://lists.apache.org/thread.html/r3d7a8303a820144f5e2d1fd0b067e18d419421b58346b53b58d3fa72%40%3Cannounce.apache.org%3E
