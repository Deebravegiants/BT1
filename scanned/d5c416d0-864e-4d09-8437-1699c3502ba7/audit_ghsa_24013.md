# [M] Moodle Open Redirect Via Error Messages

## Summary
Severity: Medium
Advisory: GHSA-hxmp-8f47-x9fc
CVE: CVE-2011-4294
CWE: CWE-601
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-hxmp-8f47-x9fc
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <1.9.13
- Packagist: `moodle/moodle` — affected >=2.0 <2.0.4
- Packagist: `moodle/moodle` — affected >=2.1 <2.1.1

## Details
The error-message functionality in Moodle 1.9.x before 1.9.13, 2.0.x before 2.0.4, and 2.1.x before 2.1.1 does not ensure that a continuation link refers to an http or https URL for the local Moodle instance, which might allow attackers to trick users into visiting arbitrary web sites via error message links that lead offsite.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4294
- https://github.com/moodle/moodle/commit/18c2fcf8f19e00f0e89421d8fd8b7486a6dc6f79
- https://github.com/moodle/moodle/commit/417fdfab6bbdcfc3f5b64704ec06912ae9cd1050
- https://github.com/moodle/moodle/commit/8f9f666c902cb30ef6f519353f38c45a29fdf4a6
- https://github.com/moodle/moodle
- http://git.moodle.org/gw?p=moodle.git;a=commit;h=8f9f666c902cb30ef6f519353f38c45a29fdf4a6
- http://moodle.org/mod/forum/discuss.php?d=182737
- http://openwall.com/lists/oss-security/2011/11/14/1
