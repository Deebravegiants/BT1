# [H] CVE-2021-4034

## Summary
Severity: High
Advisory: CVE-2021-4034
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-28
Source: https://osv.dev/vulnerability/CVE-2021-4034
Type: osv

## Details
A local privilege escalation vulnerability was found on polkit's pkexec utility. The pkexec application is a setuid tool designed to allow unprivileged users to run commands as privileged users according predefined policies. The current version of pkexec doesn't handle the calling parameters count correctly and ends trying to execute environment variables as commands. An attacker can leverage this by crafting environment variables in such a way it'll induce pkexec to execute arbitrary code. When successfully executed the attack can cause a local privilege escalation given unprivileged users administrative rights on the target machine.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2021-4034
- http://packetstormsecurity.com/files/166200/Polkit-pkexec-Privilege-Escalation.html
- https://access.redhat.com/security/vulnerabilities/RHSB-2022-001
- https://cert-portal.siemens.com/productcert/pdf/ssa-330556.pdf
- https://www.starwindsoftware.com/security/sw-20220818-0001/
- https://www.suse.com/support/kb/doc/?id=000020564
- https://bugzilla.redhat.com/show_bug.cgi?id=2025869
- https://gitlab.freedesktop.org/polkit/polkit/-/commit/a2bf5c9c83b6ae46cbd5c779d3055bff81ded683
- https://www.oracle.com/security-alerts/cpuapr2022.html
- http://packetstormsecurity.com/files/166196/Polkit-pkexec-Local-Privilege-Escalation.html
- https://www.qualys.com/2022/01/25/cve-2021-4034/pwnkit.txt
- https://www.secpod.com/blog/local-privilege-escalation-vulnerability-in-major-linux-distributions-cve-2021-4034/
- https://www.vicarius.io/vsociety/posts/pwnkit-pkexec-lpe-cve-2021-4034
