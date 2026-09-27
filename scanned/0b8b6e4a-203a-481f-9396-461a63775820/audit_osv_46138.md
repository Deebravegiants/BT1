# [M] JLSEC-2026-72

## Summary
Severity: Medium
Advisory: JLSEC-2026-72
Ecosystem: Julia
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/JLSEC-2026-72
Type: osv

## Affected
- Julia: `OpenSSH_jll` — affected >=0 <9.9.1+0

## Details
A vulnerability was found in OpenSSH when the VerifyHostKeyDNS option is enabled. A machine-in-the-middle attack can be performed by a malicious machine impersonating a legit server. This issue occurs due to how OpenSSH mishandles error codes in specific conditions when verifying the host key. For an attack to be considered successful, the attacker needs to manage to exhaust the client's memory resource first, turning the attack complexity high.

## References
- http://seclists.org/fulldisclosure/2025/Feb/18
- http://seclists.org/fulldisclosure/2025/May/7
- http://seclists.org/fulldisclosure/2025/May/8
- https://access.redhat.com/errata/RHSA-2025:16823
- https://access.redhat.com/errata/RHSA-2025:3837
- https://access.redhat.com/errata/RHSA-2025:6993
- https://access.redhat.com/errata/RHSA-2025:8385
- https://access.redhat.com/security/cve/CVE-2025-26465
- https://access.redhat.com/solutions/7109879
- https://blog.qualys.com/vulnerabilities-threat-research/2025/02/18/qualys-tru-discovers-two-vulnerabilities-in-openssh-cve-2025-26465-cve-2025-26466
- https://bugzilla.redhat.com/show_bug.cgi?id=2344780
- https://bugzilla.suse.com/show_bug.cgi?id=1237040
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://cert-portal.siemens.com/productcert/html/ssa-585531.html
- https://ftp.openbsd.org/pub/OpenBSD/patches/7.6/common/008_ssh.patch.sig
- https://lists.debian.org/debian-lts-announce/2025/02/msg00020.html
- https://lists.mindrot.org/pipermail/openssh-unix-announce/2025-February/000161.html
- https://seclists.org/oss-sec/2025/q1/144
- https://security-tracker.debian.org/tracker/CVE-2025-26465
- https://security.netapp.com/advisory/ntap-20250228-0003/
