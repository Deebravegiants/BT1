# [H] Relative Path Traversal (CWE-23) in chunked uploads in oneup/uploader-bundle

## Summary
Severity: High
Advisory: GHSA-x8wj-6m73-gfqp
CVE: CVE-2020-5237
CWE: CWE-22, CWE-23
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-02-18
Source: https://github.com/advisories/GHSA-x8wj-6m73-gfqp
Type: github-advisory

## Affected
- Packagist: `oneup/uploader-bundle` — affected >=2.0.0 <2.1.5
- Packagist: `oneup/uploader-bundle` — affected >=1.0.0 <1.9.3

## Details
### Impact
The vulnerability was identified in the web service for a chunked file
upload. While the names of the POST parameters vary with the used
frontend, their values are always used in the same way to build a path
where the chunks are stored and assembled temporarily. By not validating
these parameters properly, OneupUploaderBundle is susceptible to a path
traversal vulnerability which can be exploited to upload files to
arbitrary folders on the filesystem. The assembly process can further be
misused with some restrictions to delete and copy files to other
locations.

The vulnerability can be exploited by any users that have legitimate
access to the upload functionality and can lead to arbitrary code
execution, denial of service and disclosure of confidential information.

### Patches
Yes, see version 1.9.3 and 2.1.5.

### References
https://owasp.org/www-community/attacks/Path_Traversal

### Credits:
This security vulnerability was found by Thibaud Kehler of SySS GmbH.
E-Mail: thibaud.kehler@syss.de

## References
- https://github.com/1up-lab/OneupUploaderBundle/security/advisories/GHSA-x8wj-6m73-gfqp
- https://nvd.nist.gov/vuln/detail/CVE-2020-5237
- https://github.com/1up-lab/OneupUploaderBundle/commit/a6011449b716f163fe1ae323053077e59212350c
- https://github.com/FriendsOfPHP/security-advisories/blob/master/oneup/uploader-bundle/CVE-2020-5237.yaml
- https://www.syss.de/fileadmin/dokumente/Publikationen/Advisories/SYSS-2020-003.txt
