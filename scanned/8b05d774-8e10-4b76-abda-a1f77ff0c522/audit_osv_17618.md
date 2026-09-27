# [H] CVE-2020-17514

## Summary
Severity: High
Advisory: CVE-2020-17514
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-05-27
Source: https://osv.dev/vulnerability/CVE-2020-17514
Type: osv

## Details
Apache Fineract prior to 1.5.0 disables HTTPS hostname verification in ProcessorHelper in the configureClient method. Under typical deployments, a man in the middle attack could be successful.

## References
- https://lists.apache.org/thread.html/rc011b25289c8a6e14f8bc6d07e727382a1df3c8cf2aa5369598bbf64%40%3Cdev.fineract.apache.org%3E
- http://www.openwall.com/lists/oss-security/2021/05/27/2
- https://issues.apache.org/jira/browse/FINERACT-1211
