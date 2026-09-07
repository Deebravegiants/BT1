# [M] Keycloak vulnerable to Stored Cross site Scripting (XSS) when loading default roles

## Summary
Severity: Medium
Advisory: GHSA-w9mf-83w3-fv49
CVE: CVE-2022-2256
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-23
Source: https://github.com/advisories/GHSA-w9mf-83w3-fv49
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-parent` — affected >=0 <19.0.2

## Details
A Stored XSS vulnerability was reported in the Keycloak Security mailing list, affecting all the versions of Keycloak, including the latest release (18.0.1). The vulnerability allows a privileged attacker to execute malicious scripts in the admin console, abusing of the default roles functionality. 

### CVSS 3.1 - **3.8**

**Vector String:** AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:N

**Vector Clarification:**

* User interaction is not required as the admin console is regularly used during an administrator's work
* The scope is unchanged since the admin console web application is both the vulnerable component and where the exploit executes

### Credits

Aytaç Kalıncı, Ilker Bulgurcu, Yasin Yılmaz (@aytackalinci, @smileronin, @yasinyilmaz) - NETAŞ PENTEST TEAM

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-w9mf-83w3-fv49
- https://nvd.nist.gov/vuln/detail/CVE-2022-2256
- https://github.com/keycloak/keycloak/commit/8e705a65ab2aa2b079374ec859ee7a75fad5a7d9
- https://bugzilla.redhat.com/show_bug.cgi?id=2101942
- https://github.com/keycloak/keycloak
