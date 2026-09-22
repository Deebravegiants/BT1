# [M] Openssh: denial-of-service in openssh

## Summary
Severity: Medium
Advisory: CVE-2025-26466
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-28
Source: https://osv.dev/vulnerability/CVE-2025-26466
Type: osv

## Details
A flaw was found in the OpenSSH package. For each ping packet the SSH server receives, a pong packet is allocated in a memory buffer and stored in a queue of packages. It is only freed when the server/client key exchange has finished. A malicious client may keep sending such packages, leading to an uncontrolled increase in memory consumption on the server side. Consequently, the server may become unavailable, resulting in a denial of service attack.

## References
- http://seclists.org/fulldisclosure/2025/Feb/18
- http://seclists.org/fulldisclosure/2025/May/7
- http://seclists.org/fulldisclosure/2025/May/8
- https://access.redhat.com/downloads/content/package-browser/
- https://seclists.org/oss-sec/2025/q1/144
- https://security-tracker.debian.org/tracker/CVE-2025-26466
- https://ubuntu.com/security/CVE-2025-26466
- https://www.openssh.com/
- https://www.openwall.com/lists/oss-security/2025/02/18/1
- https://www.openwall.com/lists/oss-security/2025/02/18/4
- https://www.qualys.com/2025/02/18/openssh-mitm-dos.txt
- https://www.vicarius.io/vsociety/posts/cve-2025-26466-detection-script-memory-consumption-vulnerability-in-openssh
- https://www.vicarius.io/vsociety/posts/cve-2025-26466-mitigation-script-memory-consumption-vulnerability-in-openssh
- https://access.redhat.com/security/cve/CVE-2025-26466
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/26xxx/CVE-2025-26466.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-26466
- https://security.netapp.com/advisory/ntap-20250228-0002/
- https://bugzilla.redhat.com/show_bug.cgi?id=2345043
- https://bugzilla.suse.com/show_bug.cgi?id=1237041
- https://anongit.mindrot.org/openssh.git
