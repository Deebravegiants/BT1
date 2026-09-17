# [H] CVE-2017-14404

## Summary
Severity: High
Advisory: CVE-2017-14404
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-09-13
Source: https://osv.dev/vulnerability/CVE-2017-14404
Type: osv

## Details
The EyesOfNetwork web interface (aka eonweb) 5.1-0 allows local file inclusion via the tool_list parameter (aka the url_tool variable) to module/tool_all/select_tool.php, as demonstrated by a tool_list=php://filter/ substring.

## References
- http://www.sstrunk.com/cve/eonweb_module_tool_all_select_tool.html
