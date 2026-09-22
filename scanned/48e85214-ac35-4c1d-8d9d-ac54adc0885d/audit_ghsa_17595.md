# [H] Allure Report allows Improper XXE Restriction via DocumentBuilderFactory

## Summary
Severity: High
Advisory: GHSA-h7qf-qmf3-85qg
CVE: CVE-2025-52888
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-06-25
Source: https://github.com/advisories/GHSA-h7qf-qmf3-85qg
Type: github-advisory

## Affected
- Maven: `io.qameta.allure.plugins:xunit-xml-plugin` — affected >=0 <2.34.1
- Maven: `io.qameta.allure.plugins:junit-xml-plugin` — affected >=0 <2.34.1
- Maven: `io.qameta.allure.plugins:trx-plugin` — affected >=0 <2.34.1

## Details
### Summary
A critical XML External Entity (XXE) vulnerability exists in the xunit-xml-plugin used by Allure 2. The plugin fails to securely configure the XML parser (`DocumentBuilderFactory`) and allows external entity expansion when processing test result .xml files. This allows attackers to read arbitrary files from the file system and potentially trigger server-side request forgery (SSRF).

### Details
In `\allure2-main\plugins\xunit-xml-plugin\src\main\java\io\qameta\allure\xunitxml\XunitXmlPlugin.java` the application uses `DocumentBuilderFactory` without disabling DTDs or external entities. By generating a report with a malicious xml file within it, an attacker can perform XXE to leverage SSRF, or to read system files.

### PoC
To recreate this vulnerability, you need to install allure for command-line (In my POC I used a Windows 11 Machine). 

1. Create a folder called `allure`, and within it, create a malicious XML file. I will attach my SSRF and file reading payloads, however, for the rest of the POC, I will focus on reading system files for better screenshots.
##SSRF (replace webhook link with your own)
![image](https://github.com/user-attachments/assets/a1a9a438-b6f1-4675-973f-a43847a84519)

##Reading System Files
![image](https://github.com/user-attachments/assets/eb0e1e60-1f76-42e7-b68d-2137bed62fe9)

2. Put the malicious .xml file into the `allure` directory created previously
3. Run the following command to run the report `allure generate C:\path\to\directory\allure -o report --clean`
4. To view and confirm the executed payload, run `allure open report`
5. When the report opens, confirm the payload executedby going to `Categories > Product defects > <payload response>`
![image](https://github.com/user-attachments/assets/e7244550-2e9f-4066-b282-86f1eb8cf5e4)



### Impact
The explained XXE vulnerability can lead to Arbitrary File Disclosure and Server-Side Request Forgery. This exploitation can also be carried out silently, meaning it can be carried out without user interaction if the tool is automated within an application, and can go undetected with a carefully crafted payload. This could allow a malicious actor to view other source codes which may contain API or product keys, internal application URLs, or other secret items. This makes it an especially high risk when ran within a CI/CD platform.

## References
- https://github.com/allure-framework/allure2/security/advisories/GHSA-h7qf-qmf3-85qg
- https://nvd.nist.gov/vuln/detail/CVE-2025-52888
- https://github.com/allure-framework/allure2/commit/cbcb33719851ff70adce85d38e15d20fc58d4eb7
- https://github.com/allure-framework/allure2
