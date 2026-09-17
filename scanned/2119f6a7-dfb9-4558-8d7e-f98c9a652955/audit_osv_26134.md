# [H] CVE-2023-51767

## Summary
Severity: High
Advisory: CVE-2023-51767
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-12-24
Source: https://osv.dev/vulnerability/CVE-2023-51767
Type: osv

## Details
OpenSSH through 10.0, when common types of DRAM are used, might allow row hammer attacks (for authentication bypass) because the integer value of authenticated in mm_answer_authpassword does not resist flips of a single bit. NOTE: this is applicable to a certain threat model of attacker-victim co-location in which the attacker has user privileges. NOTE: this is disputed by the Supplier, who states "we do not consider it to be the application's responsibility to defend against platform architectural weaknesses."

## References
- http://www.openwall.com/lists/oss-security/2025/09/22/1
- http://www.openwall.com/lists/oss-security/2025/09/22/2
- http://www.openwall.com/lists/oss-security/2025/09/23/1
- http://www.openwall.com/lists/oss-security/2025/09/23/3
- http://www.openwall.com/lists/oss-security/2025/09/23/4
- http://www.openwall.com/lists/oss-security/2025/09/23/5
- http://www.openwall.com/lists/oss-security/2025/09/24/4
- http://www.openwall.com/lists/oss-security/2025/09/24/7
- http://www.openwall.com/lists/oss-security/2025/09/25/2
- http://www.openwall.com/lists/oss-security/2025/09/25/6
- http://www.openwall.com/lists/oss-security/2025/09/26/2
- http://www.openwall.com/lists/oss-security/2025/09/26/4
- http://www.openwall.com/lists/oss-security/2025/09/27/1
- http://www.openwall.com/lists/oss-security/2025/09/27/2
- http://www.openwall.com/lists/oss-security/2025/09/27/3
- http://www.openwall.com/lists/oss-security/2025/09/27/4
- http://www.openwall.com/lists/oss-security/2025/09/27/5
- http://www.openwall.com/lists/oss-security/2025/09/27/6
- http://www.openwall.com/lists/oss-security/2025/09/27/7
- http://www.openwall.com/lists/oss-security/2025/09/28/7
