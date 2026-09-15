# [M] CVE-2015-5316

## Summary
Severity: Medium
Advisory: CVE-2015-5316
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-21
Source: https://osv.dev/vulnerability/CVE-2015-5316
Type: osv

## Details
The eap_pwd_perform_confirm_exchange function in eap_peer/eap_pwd.c in wpa_supplicant 2.x before 2.6, when EAP-pwd is enabled in a network configuration profile, allows remote attackers to cause a denial of service (NULL pointer dereference and daemon crash) via an EAP-pwd Confirm message followed by the Identity exchange.

## References
- http://w1.fi/security/2015-8/eap-pwd-unexpected-confirm.txt
- http://www.openwall.com/lists/oss-security/2015/11/10/11
- http://www.securityfocus.com/bid/77538
- http://www.ubuntu.com/usn/USN-2808-1
- https://www.debian.org/security/2015/dsa-3397
- http://www.openwall.com/lists/oss-security/2015/11/10/11
- http://w1.fi/security/2015-8/eap-pwd-unexpected-confirm.txt
- http://www.openwall.com/lists/oss-security/2015/11/10/11
- http://w1.fi/security/2015-8/eap-pwd-unexpected-confirm.txt
- http://www.openwall.com/lists/oss-security/2015/11/10/11
