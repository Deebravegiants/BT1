# [H] Unrestricted Upload of File with Dangerous Type in motionEye

## Summary
Severity: High
Advisory: GHSA-m2c7-42rf-c62f
CVE: CVE-2021-44255
CWE: CWE-434
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-01
Source: https://github.com/advisories/GHSA-m2c7-42rf-c62f
Type: github-advisory

## Affected
- PyPI: `motioneye` — affected >=0

## Details
motionEye <= 0.42.1 and motioneEyeOS <= 20200606 allow a remote attacker to upload a configuration backup file containing a malicious python pickle file. This is possible when an installation is accessible over the Internet and uses no or poor authentication credentials.

The GitHub repositories for motionEye and motionEyeOS are no longer being actively maintained as of January 2022, so release of a patched version is unlikely. Keeping a motionEye or motionEyeOS installation off of the Internet and/or using strong credentials provide protection against this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-44255
- https://github.com/ccrisan/motioneyeos/issues/2843
- https://github.com/ccrisan/motioneye
- https://www.pizzapower.me/2021/10/09/self-hosted-security-part-1-motioneye
