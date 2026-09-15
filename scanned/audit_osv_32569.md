# [C] Erlang/OTP SSH Vulnerable to Pre-Authentication RCE

## Summary
Severity: Critical
Advisory: CVE-2025-32433
Aliases: GHSA-37cp-fgq5-7wc2
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-32433
Type: osv

## Details
Erlang/OTP is a set of libraries for the Erlang programming language. Prior to versions OTP-27.3.3, OTP-26.2.5.11, and OTP-25.3.2.20, a SSH server may allow an attacker to perform unauthenticated remote code execution (RCE). By exploiting a flaw in SSH protocol message handling, a malicious actor could gain unauthorized access to affected systems and execute arbitrary commands without valid credentials. This issue is patched in versions OTP-27.3.3, OTP-26.2.5.11, and OTP-25.3.2.20. A temporary workaround involves disabling the SSH server or to prevent access via firewall rules.

## References
- http://www.openwall.com/lists/oss-security/2025/04/16/2
- http://www.openwall.com/lists/oss-security/2025/04/18/1
- http://www.openwall.com/lists/oss-security/2025/04/18/2
- http://www.openwall.com/lists/oss-security/2025/04/18/6
- http://www.openwall.com/lists/oss-security/2025/04/19/1
- https://lists.debian.org/debian-lts-announce/2025/04/msg00028.html
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2025-32433
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32433.json
- https://github.com/erlang/otp/security/advisories/GHSA-37cp-fgq5-7wc2
- https://nvd.nist.gov/vuln/detail/CVE-2025-32433
- https://sec.cloudapps.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-erlang-otp-ssh-xyZZy
- https://security.netapp.com/advisory/ntap-20250425-0001/
- https://github.com/erlang/otp/commit/0fcd9c56524b28615e8ece65fc0c3f66ef6e4c12
- https://github.com/erlang/otp/commit/6eef04130afc8b0ccb63c9a0d8650209cf54892f
- https://github.com/erlang/otp/commit/b1924d37fd83c070055beb115d5d6a6a9490b891
- https://github.com/ProDefense/CVE-2025-32433/blob/main/CVE-2025-32433.py
