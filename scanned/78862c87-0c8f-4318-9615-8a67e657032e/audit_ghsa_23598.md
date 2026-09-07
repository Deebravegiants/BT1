# [M] Moodle  Authenticated Spelling Binary Remote Code Execution

## Summary
Severity: Medium
Advisory: GHSA-wxqg-fg7v-mmc6
CVE: CVE-2013-3630
CWE: CWE-94
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-wxqg-fg7v-mmc6
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <2.5.3

## Details
Moodle through 2.5.2 allows remote authenticated administrators to execute arbitrary programs by configuring the aspell pathname and then triggering a spell-check operation within the TinyMCE editor.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-3630
- https://community.rapid7.com/community/metasploit/blog/2013/10/30/seven-foss-disclosures-part-one
- https://community.rapid7.com/community/metasploit/blog/2013/10/30/seven-tricks-and-treats
- https://github.com/moodle/moodle
- http://packetstormsecurity.com/files/164479/Moodle-Authenticated-Spelling-Binary-Remote-Code-Execution.html
