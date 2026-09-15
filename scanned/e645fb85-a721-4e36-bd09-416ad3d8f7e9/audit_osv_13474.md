# [C] CVE-2018-1999022

## Summary
Severity: Critical
Advisory: CVE-2018-1999022
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-23
Source: https://osv.dev/vulnerability/CVE-2018-1999022
Type: osv

## Details
PEAR HTML_QuickForm version 3.2.14 contains an eval injection (CWE-95) vulnerability in HTML_QuickForm's getSubmitValue method, HTML_QuickForm's validate method, HTML_QuickForm_hierselect's _setOptions method, HTML_QuickForm_element's _findValue method, HTML_QuickForm_element's _prepareValue method. that can result in Possible information disclosure, possible impact on data integrity and execution of arbitrary code. This attack appear to be exploitable via A specially crafted query string could be utilised, e.g. http://www.example.com/admin/add_practice_type_id[1]=fubar%27])%20OR%20die(%27OOK!%27);%20//&mode=live. This vulnerability appears to have been fixed in 3.2.15.

## References
- http://blog.pear.php.net/2018/07/19/security-vulnerability-announcement-html_quickform/
- https://civicrm.org/advisory/civi-sa-2018-07-remote-code-execution-in-quickform
