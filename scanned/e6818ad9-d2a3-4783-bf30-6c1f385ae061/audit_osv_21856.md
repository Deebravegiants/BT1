# [H] CVE-2022-0484

## Summary
Severity: High
Advisory: CVE-2022-0484
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-02-04
Source: https://osv.dev/vulnerability/CVE-2022-0484
Type: osv

## Details
Lack of validation of URLs causes Mirantis Container Cloud Lens Extension before v3.1.1 to open external programs other than the default browser to perform sign on to a new cluster. An attacker could host a webserver which serves a malicious Mirantis Container Cloud configuration file and induce the victim to add a new cluster via its URL. This issue affects: Mirantis Mirantis Container Cloud Lens Extension v3 versions prior to v3.1.1.

## References
- https://github.com/Mirantis/security/blob/main/advisories/0005.md
