# [H] Multiple XXE vulnerabilities in OBS

## Summary
Severity: High
Advisory: CVE-2022-21949
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-05-03
Source: https://osv.dev/vulnerability/CVE-2022-21949
Type: osv

## Details
A Improper Restriction of XML External Entity Reference vulnerability in SUSE Open Build Service allows remote attackers to reference external entities in certain operations. This can be used to gain information from the server that can be abused to escalate to Admin privileges on OBS. This issue affects: SUSE Open Build Service Open Build Service versions prior to 2.10.13.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/21xxx/CVE-2022-21949.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-21949
- https://bugzilla.suse.com/show_bug.cgi?id=1197928
