# [H] CVE-2019-11444

## Summary
Severity: High
Advisory: CVE-2019-11444
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-22
Source: https://osv.dev/vulnerability/CVE-2019-11444
Type: osv

## Details
An issue was discovered in Liferay Portal CE 7.1.2 GA3. An attacker can use Liferay's Groovy script console to execute OS commands. Commands can be executed via a [command].execute() call, as demonstrated by "def cmd =" in the ServerAdminPortlet_script value to group/control_panel/manage. Valid credentials for an application administrator user account are required. NOTE: The developer disputes this as a vulnerability since it is a feature for administrators to run groovy scripts and therefore not a design flaw

## References
- https://dev.liferay.com/discover/portal/-/knowledge_base/7-1/running-scripts-from-the-script-console
- https://pentest.com.tr/exploits/Liferay-CE-Portal-Tomcat-7-1-2-ga3-Groovy-Console-Remote-Command-Execution-Metasploit.html
- https://www.exploit-db.com/exploits/46525
