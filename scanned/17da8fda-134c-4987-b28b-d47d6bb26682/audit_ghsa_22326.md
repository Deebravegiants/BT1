# [M] Moodle allows attackers to enter additional answer attempts

## Summary
Severity: Medium
Advisory: GHSA-mm9q-3847-m48x
CVE: CVE-2015-5264
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-mm9q-3847-m48x
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.7.0 <2.7.10
- Packagist: `moodle/moodle` — affected >=2.8.0 <2.8.8
- Packagist: `moodle/moodle` — affected >=2.9.0 <2.9.2

## Details
The lesson module in Moodle through 2.6.11, 2.7.x before 2.7.10, 2.8.x before 2.8.8, and 2.9.x before 2.9.2 allows remote authenticated users to bypass intended access restrictions and enter additional answer attempts by leveraging the student role.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5264
- https://github.com/moodle/moodle/commit/3071f085918dfeabb154596362dab2648ec6ad84
- https://github.com/moodle/moodle/commit/343ed5b929ff8a68efe076505cd3e52d951f7869
- https://github.com/moodle/moodle/commit/39b50f7d3eea43266a3d0c09590e48624e69a091
- https://github.com/moodle/moodle/commit/67e3f70bb11382fc0f1eaf1a160c349269e370cc
- https://github.com/moodle/moodle/commit/9d5b339126586eddeced463c81295146e231a3c4
- https://github.com/moodle/moodle/commit/9fd13426926fd882d3f024cb7171802ef2b3814d
- https://github.com/moodle/moodle/commit/ca74203efd51be6467091d9af762a31a7cad5840
- https://github.com/moodle/moodle/commit/cd3a6a78b67abf5c9eb355ddc7899b1b2a9b20ac
- https://github.com/moodle/moodle/commit/e7288eaabe77e04157f702b20fd0a7e9ce7067ca
- https://github.com/moodle/moodle/commit/f9cc721dfd761ee34209cf58838079b9b550b356
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=320287
- https://web.archive.org/web/20160323063809/http://www.securitytracker.com/id/1033619
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-50516
- http://www.openwall.com/lists/oss-security/2015/09/21/1
