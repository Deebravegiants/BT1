# [C] Apache Druid Vulnerable to Authentication Bypass

## Summary
Severity: Critical
Advisory: GHSA-q672-hfc7-g833
CVE: CVE-2026-23906
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-10
Source: https://github.com/advisories/GHSA-q672-hfc7-g833
Type: github-advisory

## Affected
- Maven: `org.apache.druid.extensions:druid-basic-security` — affected >=0.17.0 <36.0.0

## Details
Affected Products and Versions
  *  Apache Druid
  *  Affected Versions: 0.17.0 through 35.x (all versions prior to 36.0.0)
  *  Prerequisites:  *  druid-basic-security extension enabled
  *  LDAP authenticator configured
  *  Underlying LDAP server permits anonymous bind                                                                                                                                                   






Vulnerability Description

An authentication bypass vulnerability exists in Apache Druid when using the druid-basic-security extension with LDAP authentication. If the underlying LDAP server is configured to allow anonymous
binds, an attacker can bypass authentication by providing an existing username with an empty password. This allows unauthorized access to otherwise restricted Druid resources without valid credentials.

The vulnerability stems from improper validation of LDAP authentication responses when anonymous binds are permitted, effectively treating anonymous bind success as valid user authentication. 

Impact

A remote, unauthenticated attacker can:
  *  Gain unauthorized access to the Apache Druid cluster
  *  Access sensitive data stored in Druid datasources
  *  Execute queries and potentially manipulate data
  *  Access administrative interfaces if the bypassed account has elevated privileges
  *  Completely compromise the confidentiality, integrity, and availability of the Druid deployment                                                                                                                                                                                    


Mitigation
 
Immediate Mitigation (No Druid Upgrade Required):                                                                                                                                                    
  *  Disable anonymous bind on your LDAP server. This prevents the vulnerability from being exploitable and is the recommended immediate action.



Resolution
  *  Upgrade Apache Druid to version 36.0.0 or later, which includes fixes to properly reject anonymous LDAP bind attempts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-23906
- https://github.com/apache/druid
- https://lists.apache.org/thread/2x9rv3kv6t1p577lvq4z0rl0zlt9g4sr
- http://www.openwall.com/lists/oss-security/2026/02/09/5
