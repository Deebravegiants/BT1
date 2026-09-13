# [M] CVE-2021-40375

## Summary
Severity: Medium
Advisory: CVE-2021-40375
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-04-06
Source: https://osv.dev/vulnerability/CVE-2021-40375
Type: osv

## Details
Apperta Foundation OpenEyes 3.5.1 allows remote attackers to view the sensitive information of patients without having the intended level of privilege. Despite OpenEyes returning a Forbidden error message, the contents of a patient's profile are still returned in the server response. This response can be read in an intercepting proxy or by viewing the page source. Sensitive information returned in responses includes patient PII and medication records or history.

## References
- https://openeyes.apperta.org/
- https://github.com/DCKento/CVE-2021-40375
