# [M] Attribute Injection leading to XSS(Cross-Site-Scripting)

## Summary
Severity: Medium
Advisory: GHSA-v4v2-8h88-65qj
CVE: CVE-2023-49276
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-11-24
Source: https://github.com/advisories/GHSA-v4v2-8h88-65qj
Type: github-advisory

## Affected
- npm: `uptime-kuma` — affected >=1.20.0 <1.23.7

## Details
### Summary
Google Analytics element Attribute Injection leading to XSS

### Details
Since the custom status interface can set an independent Google Analytics ID and the template has not been sanitized, there is an attribute injection vulnerability here, which can lead to XSS attacks.
![image](https://user-images.githubusercontent.com/110759348/282278047-667b774b-421f-449a-8f95-3f3906ae4216.png)

### PoC
1. Run the latest version of the louislam/uptime-kuma container and initialize the account password.
2. Create a new status page.
3. Edit the status page and change the Google Analytics ID to following payload(it only works for firefox. Any attribute can be injected, but this seems the most intuitive):
```
123123" onafterscriptexecute=alert(window.name+1),eval(window.name) a="x
```

4. Click Save and return to the interface. XSS occurs.
screenshots:
![image](https://user-images.githubusercontent.com/110759348/282287393-4874974f-9416-4941-9c2e-a92ee2412197.png)

![9d0603e634fb7da2e83a0a45dc0a36ac](https://user-images.githubusercontent.com/110759348/282287346-1deb0382-520f-47cf-b191-9b7d19c47879.png)

## References
- https://github.com/louislam/uptime-kuma/security/advisories/GHSA-v4v2-8h88-65qj
- https://nvd.nist.gov/vuln/detail/CVE-2023-49276
- https://github.com/louislam/uptime-kuma/commit/f28dccf4e11f041564293e4f407e69ab9ee2277f
- https://github.com/louislam/uptime-kuma
