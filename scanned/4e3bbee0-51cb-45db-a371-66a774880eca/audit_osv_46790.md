# [H] CVE-2015-3193

## Summary
Severity: High
Advisory: CVE-2015-3193
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2015-12-06
Source: https://osv.dev/vulnerability/CVE-2015-3193
Type: osv

## Details
The Montgomery squaring implementation in crypto/bn/asm/x86_64-mont5.pl in OpenSSL 1.0.2 before 1.0.2e on the x86_64 platform, as used by the BN_mod_exp function, mishandles carry propagation and produces incorrect output, which makes it easier for remote attackers to obtain sensitive private-key information via an attack against use of a (1) Diffie-Hellman (DH) or (2) Diffie-Hellman Ephemeral (DHE) ciphersuite.

## References
- http://fortiguard.com/advisory/openssl-advisory-december-2015
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10759
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10761
- http://openssl.org/news/secadv/20151203.txt
- http://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-20151204-openssl
- http://www.fortiguard.com/advisory/openssl-advisory-december-2015
- http://www.oracle.com/technetwork/security-advisory/cpuapr2016v3-2985753.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2016-2881720.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2017-3236626.html
- http://www.securityfocus.com/bid/78705
- http://www.securityfocus.com/bid/91787
- http://www.securitytracker.com/id/1034294
- http://www.slackware.com/security/viewer.php?l=slackware-security&y=2015&m=slackware-security.539966
- http://www.slackware.com/security/viewer.php?l=slackware-security&y=2015&m=slackware-security.754583
- http://www.ubuntu.com/usn/USN-2830-1
- https://blog.fuzzing-project.org/31-Fuzzing-Math-miscalculations-in-OpenSSLs-BN_mod_exp-CVE-2015-3193.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1288317
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05398322
- https://kb.isc.org/article/AA-01438
- https://kb.pulsesecure.net/articles/Pulse_Security_Advisories/SA40100
