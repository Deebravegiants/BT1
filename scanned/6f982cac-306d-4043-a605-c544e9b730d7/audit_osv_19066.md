# [H] CVE-2020-6817

## Summary
Severity: High
Advisory: CVE-2020-6817
Aliases: GHSA-vqhp-cxgc-6wmm, PYSEC-2020-340, SNYK-PYTHON-BLEACH-561754
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-16
Source: https://osv.dev/vulnerability/CVE-2020-6817
Type: osv

## Details
bleach.clean behavior parsing style attributes could result in a regular expression denial of service (ReDoS). Calls to bleach.clean with an allowed tag with an allowed style attribute are vulnerable to ReDoS. For example, bleach.clean(..., attributes={'a': ['style']}).

## References
- https://github.com/mozilla/bleach/security/advisories/GHSA-vqhp-cxgc-6wmm
- https://bugzilla.mozilla.org/show_bug.cgi?id=1623633
