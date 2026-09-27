# [H] CVE-2020-8131

## Summary
Severity: High
Advisory: CVE-2020-8131
Aliases: GHSA-8mfc-v7wv-p62g
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-02-24
Source: https://osv.dev/vulnerability/CVE-2020-8131
Type: osv

## Details
Arbitrary filesystem write vulnerability in Yarn before 1.22.0 allows attackers to write to any path on the filesystem and potentially lead to arbitrary code execution by forcing the user to install a malicious package.

## References
- https://github.com/yarnpkg/yarn/pull/7831
- https://hackerone.com/reports/730239
