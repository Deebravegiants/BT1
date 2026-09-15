# [M] C5 Firefly III CSV Injection.

## Summary
Severity: Medium
Advisory: GHSA-29w6-c52g-m8jc
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-01-31
Source: https://github.com/advisories/GHSA-29w6-c52g-m8jc
Type: github-advisory

## Affected
- Packagist: `grumpydictator/firefly-iii` — affected >=0 <6.1.7

## Details
### Summary
CSV injection is a vulnerability where untrusted user input in CSV files can lead to unauthorized access or data manipulation. 
In my subsequent testing of the application.

### Details
I discovered that there is an option to "Export Data" from the web app to your personal computer, which exports a "csv" file that can be opened with Excel software that supports macros.

P.S 
I discovered that the web application's is offering a demo-site that anyone may access to play with the web application. So, there's a chance that someone will export the data (CVS) from the demo site and execute it on their PC, giving the malicious actor a complete control over their machine. (if a user enters a malicious payload to the website).

### PoC
You can check out my vulnerability report if you need more details/PoC with screenshots: (removed by JC5)

### Impact
An attacker can exploit this by entering a specially crafted payload to one of the fields, and when a user export the csv file using the "Export Data" function, the attacker can potentiality can RCE.

### Addendum by JC5, the developer of Firefly III
There is zero impact on normal users, even on vulnerable versions.

## References
- https://github.com/firefly-iii/firefly-iii/security/advisories/GHSA-29w6-c52g-m8jc
- https://github.com/firefly-iii/firefly-iii
