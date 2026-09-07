# [M] Moodle allows remote authenticated users to cause a denial of service (invalid database records)

## Summary
Severity: Medium
Advisory: GHSA-fhgh-fjh9-vq62
CVE: CVE-2011-4292
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-fhgh-fjh9-vq62
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.0.0 <2.0.3

## Details
Moodle 2.0.x before 2.0.3 allows remote authenticated users to cause a denial of service (invalid database records) via a series of crafted comments operations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4292
- http://git.moodle.org
- http://git.moodle.org/gw?p=moodle.git%3Ba=commit%3Bh=acb4688d29a7cc028803ee3d81edc7f1b6515c64
- http://git.moodle.org/gw?p=moodle.git;a=commit;h=acb4688d29a7cc028803ee3d81edc7f1b6515c64
- http://moodle.org/mod/forum/discuss.php?d=175594
- http://openwall.com/lists/oss-security/2011/11/14/1
