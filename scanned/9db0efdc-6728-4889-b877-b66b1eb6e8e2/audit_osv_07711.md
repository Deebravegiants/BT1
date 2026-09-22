# [M] Apache Tomcat: FileUpload: DoS due to accumulation of temporary files on Windows

## Summary
Severity: Medium
Advisory: BIT-tomcat-2023-42794
Aliases: CVE-2023-42794, GHSA-jm7m-8jh6-29hp
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tomcat-2023-42794
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=9.0.70 <9.0.81

## Details
Incomplete Cleanup vulnerability in Apache Tomcat.

The internal fork of Commons FileUpload packaged with Apache Tomcat 9.0.70 through 9.0.80 and 8.5.85 through 8.5.93 included an unreleased, 
in progress refactoring that exposed a potential denial of service on 
Windows if a web application opened a stream for an uploaded file but 
failed to close the stream. The file would never be deleted from disk 
creating the possibility of an eventual denial of service due to the 
disk being full.

Other, EOL versions may also be affected.


Users are recommended to upgrade to version 9.0.81 onwards or 8.5.94 onwards, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2023/10/10/8
- https://lists.apache.org/thread/vvbr2ms7lockj1hlhz5q3wmxb2mwcw82
- https://nvd.nist.gov/vuln/detail/CVE-2023-42794
