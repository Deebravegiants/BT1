# [H] Uncontrolled Resource Consumption in cmark-gfm

## Summary
Severity: High
Advisory: CVE-2022-39209
Aliases: GHSA-cgh3-p57x-9q7q
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-09-15
Source: https://osv.dev/vulnerability/CVE-2022-39209
Type: osv

## Details
cmark-gfm is GitHub's fork of cmark, a CommonMark parsing and rendering library and program in C. In versions prior to 0.29.0.gfm.6 a polynomial time complexity issue in cmark-gfm's autolink extension may lead to unbounded resource exhaustion and subsequent denial of service. Users may verify the patch by running `python3 -c 'print("![l"* 100000 + "\n")' | ./cmark-gfm -e autolink`, which will resource exhaust on unpatched cmark-gfm but render correctly on patched cmark-gfm. This vulnerability has been patched in 0.29.0.gfm.6. Users are advised to upgrade. Users unable to upgrade should disable the use of the autolink extension.

## References
- https://en.wikipedia.org/wiki/Time_complexity
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39209.json
- https://github.com/github/cmark-gfm/security/advisories/GHSA-cgh3-p57x-9q7q
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JIUCZN3PEKUCT2JQYQTYOVIJG2KSD6G7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JMGP65NANDVKPDMXMKYO2ZV2H2HZJY4P/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UEAAAI4OULDYQ2TA3HOXH54PC3DCBFZS/
- https://nvd.nist.gov/vuln/detail/CVE-2022-39209
- https://github.com/github/cmark-gfm/commit/9d57d8a23142b316282bdfc954cb0ecda40a8655
