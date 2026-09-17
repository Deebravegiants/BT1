# [H] October CMS Local File Inclusion

## Summary
Severity: High
Advisory: GHSA-v7cr-w5v6-6659
CVE: CVE-2018-1999009
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-v7cr-w5v6-6659
Type: github-advisory

## Affected
- Packagist: `october/october` — affected >=0 <1.0.437

## Details
October CMS version prior to Build 437 contains a Local File Inclusion vulnerability in [modules/system/traits/ViewMaker.php](https://github.com/octobercms/october/blob/v1.0.436/modules/system/traits/ViewMaker.php#L244) (makeFileContents function) that can result in Sensitive information disclosure and remote code execution. This attack appear to be exploitable remotely if the /backend path is accessible. This vulnerability appears to have been fixed in Build 437.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1999009
- https://github.com/octobercms/october
- http://octobercms.com/support/article/rn-10
