# [M] Openssh: machine-in-the-middle attack if verifyhostkeydns is enabled

## Summary
Severity: Medium
Advisory: CVE-2025-26465
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2025-02-18
Source: https://osv.dev/vulnerability/CVE-2025-26465
Type: osv

## Details
A vulnerability was found in OpenSSH when the VerifyHostKeyDNS option is enabled. A machine-in-the-middle attack can be performed by a malicious machine impersonating a legit server. This issue occurs due to how OpenSSH mishandles error codes in specific conditions when verifying the host key. For an attack to be considered successful, the attacker needs to manage to exhaust the client's memory resource first, turning the attack complexity high.

## References
- http://seclists.org/fulldisclosure/2025/Feb/18
- http://seclists.org/fulldisclosure/2025/May/7
- http://seclists.org/fulldisclosure/2025/May/8
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/solutions/7109879
- https://catalog.redhat.com/software/containers/
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://cert-portal.siemens.com/productcert/html/ssa-585531.html
- https://ftp.openbsd.org/pub/OpenBSD/patches/7.6/common/008_ssh.patch.sig
- https://lists.debian.org/debian-lts-announce/2025/02/msg00020.html
- https://lists.mindrot.org/pipermail/openssh-unix-announce/2025-February/000161.html
- https://seclists.org/oss-sec/2025/q1/144
- https://security-tracker.debian.org/tracker/CVE-2025-26465
- https://ubuntu.com/security/CVE-2025-26465
- https://www.openssh.com/
- https://www.openssh.com/releasenotes.html#9.9p2
- https://www.openwall.com/lists/oss-security/2025/02/18/1
- https://www.openwall.com/lists/oss-security/2025/02/18/4
- https://www.theregister.com/2025/02/18/openssh_vulnerabilities_mitm_dos/
- https://www.vicarius.io/vsociety/posts/cve-2025-26465-detect-vulnerable-openssh
