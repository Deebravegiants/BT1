# [M] CVE-2021-3634

## Summary
Severity: Medium
Advisory: CVE-2021-3634
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-31
Source: https://osv.dev/vulnerability/CVE-2021-3634
Type: osv

## Details
A flaw has been found in libssh in versions prior to 0.9.6. The SSH protocol keeps track of two shared secrets during the lifetime of the session. One of them is called secret_hash and the other session_id. Initially, both of them are the same, but after key re-exchange, previous session_id is kept and used as an input to new secret_hash. Historically, both of these buffers had shared length variable, which worked as long as these buffers were same. But the key re-exchange operation can also change the key exchange method, which can be based on hash of different size, eventually creating "secret_hash" of different size than the session_id has. This becomes an issue when the session_id memory is zeroed or when it is used again during second key re-exchange.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DRK67AJCWYYVAGF5SGAHNZXCX3PN3ZFP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JKYD3ZRAMDAQX3ZW6THHUF3GXN7FF6B4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SVWAAB2XMKEUMPMDALINKAA4U2QM4LNG/
- https://security.gentoo.org/glsa/202312-05
- https://security.netapp.com/advisory/ntap-20211004-0003/
- https://www.debian.org/security/2021/dsa-4965
- https://bugzilla.redhat.com/show_bug.cgi?id=1978810
- https://www.oracle.com/security-alerts/cpujan2022.html
