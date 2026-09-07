# [C] Rubyzip gem contains a Directory Traversal vulnerability in zip file component

## Summary
Severity: Critical
Advisory: GHSA-vqcq-mrmw-mcmg
CVE: CVE-2018-1000544
CWE: CWE-434, CWE-59
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-09-06
Source: https://github.com/advisories/GHSA-vqcq-mrmw-mcmg
Type: github-advisory

## Affected
- RubyGems: `rubyzip` — affected >=0 <1.2.2

## Details
rubyzip gem rubyzip version 1.2.1 and earlier contains a Directory Traversal vulnerability in Zip::File component that can result in write arbitrary files to the filesystem. This attack appear to be exploitable via If a site allows uploading of .zip files , an attacker can upload a malicious file that contains symlinks or files with absolute pathnames "../" to write arbitrary files to the filesystem..

This is similar to CVE-2017-5946 which was patched in 1.2.1 but the fix in that case was incomplete.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000544
- https://github.com/rubyzip/rubyzip/issues/369
- https://access.redhat.com/errata/RHSA-2018:3466
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rubyzip/CVE-2018-1000544.yml
- https://github.com/rubyzip/rubyzip
- https://lists.debian.org/debian-lts-announce/2018/08/msg00013.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00002.html
