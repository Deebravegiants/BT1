# [H] CVE-2017-7411

## Summary
Severity: High
Advisory: CVE-2017-7411
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-10-30
Source: https://osv.dev/vulnerability/CVE-2017-7411
Type: osv

## Details
An issue was discovered in Enalean Tuleap 9.6 and prior versions. The vulnerability exists because the User::getRecentElements() method is using the unserialize() function with a preference value that can be arbitrarily manipulated by malicious users through the REST API interface, and this can be exploited to inject arbitrary PHP objects into the application scope, allowing an attacker to perform a variety of attacks (including but not limited to Remote Code Execution).

## References
- https://www.exploit-db.com/exploits/43374/
- http://karmainsecurity.com/KIS-2017-02
- http://packetstormsecurity.com/files/144716/Tuleap-9.6-Second-Order-PHP-Object-Injection.html
- http://seclists.org/fulldisclosure/2017/Oct/53
- http://www.openwall.com/lists/oss-security/2017/10/23/3
- https://tuleap.net/plugins/tracker/?aid=10118
