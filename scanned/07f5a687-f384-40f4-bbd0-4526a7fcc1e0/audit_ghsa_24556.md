# [H] TeamPass arbitrary file upload vulnerability

## Summary
Severity: High
Advisory: GHSA-rm3q-qfrm-frrv
CVE: CVE-2017-15054
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-rm3q-qfrm-frrv
Type: github-advisory

## Affected
- Packagist: `nilsteampassnet/teampass` — affected >=0 <2.1.27.9

## Details
An arbitrary file upload vulnerability, present in TeamPass before 2.1.27.9, allows remote authenticated users to upload arbitrary files leading to Remote Command Execution. To exploit this vulnerability, an authenticated attacker has to tamper with parameters of a request to upload.files.php, in order to select the correct branch and be able to upload any arbitrary file. From there, it can simply access the file to execute code on the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15054
- https://github.com/nilsteampassnet/TeamPass/commit/9811c9d453da4bd1101ff7033250d1fbedf101fc
- https://github.com/nilsteampassnet/TeamPass
- http://blog.amossys.fr/teampass-multiple-cve-01.html
