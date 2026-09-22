# [M] CVE-2020-6107

## Summary
Severity: Medium
Advisory: CVE-2020-6107
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2020-10-15
Source: https://osv.dev/vulnerability/CVE-2020-6107
Type: osv

## Details
An exploitable information disclosure vulnerability exists in the dev_read functionality of F2fs-Tools F2fs.Fsck 1.13. A specially crafted f2fs filesystem can cause an uninitialized read resulting in an information disclosure. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://security.gentoo.org/glsa/202101-26
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1049
