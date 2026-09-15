# [M] Systemd-coredump: race condition that allows a local attacker to crash a suid program and gain read access to the resulting core dump

## Summary
Severity: Medium
Advisory: CVE-2025-4598
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-05-30
Source: https://osv.dev/vulnerability/CVE-2025-4598
Type: osv

## Details
A vulnerability was found in systemd-coredump. This flaw allows an attacker to force a SUID process to crash and replace it with a non-SUID binary to access the original's privileged process coredump, allowing the attacker to read sensitive data, such as /etc/shadow content, loaded by the original process.

A SUID binary or process has a special type of permission, which allows the process to run with the file owner's permissions, regardless of the user executing the binary. This allows the process to access more restricted data than unprivileged users or processes would be able to. An attacker can leverage this flaw by forcing a SUID process to crash and force the Linux kernel to recycle the process PID before systemd-coredump can analyze the /proc/pid/auxv file. If the attacker wins the race condition, they gain access to the original's SUID process coredump file. They can read sensitive content loaded into memory by the original binary, affecting data confidentiality.

## References
- http://seclists.org/fulldisclosure/2025/Jun/9
- http://www.openwall.com/lists/oss-security/2025/06/05/1
- http://www.openwall.com/lists/oss-security/2025/06/05/3
- http://www.openwall.com/lists/oss-security/2025/08/18/3
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://lists.debian.org/debian-lts-announce/2025/07/msg00022.html
- https://www.openwall.com/lists/oss-security/2025/05/29/3
- https://www.openwall.com/lists/oss-security/2025/08/18/3
- https://access.redhat.com/errata/RHSA-2025:22660
- https://access.redhat.com/errata/RHSA-2025:22868
- https://access.redhat.com/errata/RHSA-2025:23227
- https://access.redhat.com/errata/RHSA-2025:23234
- https://access.redhat.com/errata/RHSA-2026:0414
- https://access.redhat.com/errata/RHSA-2026:1652
- https://access.redhat.com/errata/RHSA-2026:18153
- https://access.redhat.com/security/cve/CVE-2025-4598
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/4xxx/CVE-2025-4598.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-4598
