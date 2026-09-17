# [M] CVE-2016-20012

## Summary
Severity: Medium
Advisory: CVE-2016-20012
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-09-15
Source: https://osv.dev/vulnerability/CVE-2016-20012
Type: osv

## Details
OpenSSH through 8.7 allows remote attackers, who have a suspicion that a certain combination of username and public key is known to an SSH server, to test whether this suspicion is correct. This occurs because a challenge is sent only when that combination could be valid for a login session. NOTE: the vendor does not recognize user enumeration as a vulnerability for this product

## References
- https://security.netapp.com/advisory/ntap-20211014-0005/
- https://utcc.utoronto.ca/~cks/space/blog/tech/SSHKeysAreInfoLeak
- https://www.openwall.com/lists/oss-security/2018/08/24/1
- https://github.com/openssh/openssh-portable/pull/270#issuecomment-920577097
- https://github.com/openssh/openssh-portable/pull/270#issuecomment-943909185
- https://github.com/openssh/openssh-portable/pull/270
- https://github.com/openssh/openssh-portable/blob/d0fffc88c8fe90c1815c6f4097bc8cbcabc0f3dd/auth2-pubkey.c#L261-L265
- https://rushter.com/blog/public-ssh-keys/
