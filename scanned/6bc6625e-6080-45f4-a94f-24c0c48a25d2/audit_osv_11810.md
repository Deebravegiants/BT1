# [C] CVE-2017-9807

## Summary
Severity: Critical
Advisory: CVE-2017-9807
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-22
Source: https://osv.dev/vulnerability/CVE-2017-9807
Type: osv

## Details
An issue was discovered in the OpenWebif plugin through 1.2.4 for E2 open devices. The saveConfig function of "plugin/controllers/models/config.py" performs an eval() call on the contents of the "key" HTTP GET parameter. This allows an unauthenticated remote attacker to execute arbitrary Python code or OS commands via api/saveconfig.

## References
- http://www.openwall.com/lists/oss-security/2017/10/02/4
- https://census-labs.com/news/2017/10/02/e2openplugin-openwebif-saveconfig-remote-code-execution/
- http://www.securityfocus.com/bid/99232
- https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/issues/620
