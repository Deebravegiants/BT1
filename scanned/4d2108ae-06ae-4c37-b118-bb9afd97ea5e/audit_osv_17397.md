# [H] CVE-2020-15012

## Summary
Severity: High
Advisory: CVE-2020-15012
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2020-10-12
Source: https://osv.dev/vulnerability/CVE-2020-15012
Type: osv

## Details
A Directory Traversal issue was discovered in Sonatype Nexus Repository Manager 2.x before 2.14.19. A user that requests a crafted path can traverse up the file system to get access to content on disk (that the user running nxrm also has access to).

## References
- https://support.sonatype.com/hc/en-us/articles/360051068253
