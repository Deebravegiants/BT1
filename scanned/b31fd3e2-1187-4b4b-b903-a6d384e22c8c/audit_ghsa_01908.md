# [M] Code injection in plupload

## Summary
Severity: Medium
Advisory: GHSA-rp2c-jrgp-cvr8
CVE: CVE-2021-23562
CWE: CWE-434, CWE-75
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-12-16
Source: https://github.com/advisories/GHSA-rp2c-jrgp-cvr8
Type: github-advisory

## Affected
- npm: `plupload` — affected >=0 <2.3.9

## Details
This affects the package plupload before 2.3.9. A file name containing JavaScript code could be uploaded and run. An attacker would need to trick a user to upload this kind of file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23562
- https://github.com/moxiecode/plupload/commit/d12175d4b5fa799b994ee1bb17bfbeec55b386fb
- https://github.com/moxiecode/plupload
- https://github.com/moxiecode/plupload/blob/master/js/jquery.plupload.queue/jquery.plupload.queue.js%23L226
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARS-2306665
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWER-2306663
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWERGITHUBMOXIECODE-2306664
- https://snyk.io/vuln/SNYK-JS-PLUPLOAD-1583909
