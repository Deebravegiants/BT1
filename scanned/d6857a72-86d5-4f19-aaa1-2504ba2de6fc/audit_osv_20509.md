# [C] CVE-2021-34427

## Summary
Severity: Critical
Advisory: CVE-2021-34427
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-25
Source: https://osv.dev/vulnerability/CVE-2021-34427
Type: osv

## Details
In Eclipse BIRT versions 4.8.0 and earlier, an attacker can use query parameters to create a JSP file which is accessible from remote (current BIRT viewer dir) to inject JSP code into the running instance.

## References
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=538142
- http://packetstormsecurity.com/files/170326/Eclipse-Business-Intelligence-Reporting-Tool-4.11.0-Remote-Code-Execution.html
- http://seclists.org/fulldisclosure/2022/Dec/30
