# [C] CVE-2012-6706

## Summary
Severity: Critical
Advisory: CVE-2012-6706
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-22
Source: https://osv.dev/vulnerability/CVE-2012-6706
Type: osv

## Details
A VMSF_DELTA memory corruption was discovered in unrar before 5.5.5, as used in Sophos Anti-Virus Threat Detection Engine before 3.37.2 and other products, that can lead to arbitrary code execution. An integer overflow can be caused in DataSize+CurChannel. The result is a negative value of the "DestPos" variable, which allows the attacker to write out of bounds when setting Mem[DestPos].

## References
- http://securitytracker.com/id?1027725
- http://telussecuritylabs.com/threats/show/TSL20121207-01
- https://bugs.chromium.org/p/project-zero/issues/detail?id=1286
- https://community.sophos.com/kb/en-us/118424#six
- https://lock.cmpxchg8b.com/sophailv2.pdf
- https://nakedsecurity.sophos.com/2012/11/05/tavis-ormandy-sophos/
- https://security.gentoo.org/glsa/201708-05
- https://security.gentoo.org/glsa/201709-24
- https://security.gentoo.org/glsa/201804-16
- https://bugs.chromium.org/p/project-zero/issues/detail?id=1286
- https://kc.mcafee.com/corporate/index?page=content&id=SB10205
