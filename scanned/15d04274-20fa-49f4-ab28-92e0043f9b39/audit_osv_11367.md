# [C] CVE-2017-7550

## Summary
Severity: Critical
Advisory: CVE-2017-7550
Aliases: GHSA-588w-w6mv-3cw5, PYSEC-2017-4
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-21
Source: https://osv.dev/vulnerability/CVE-2017-7550
Type: osv

## Details
A flaw was found in the way Ansible (2.3.x before 2.3.3, and 2.4.x before 2.4.1) passed certain parameters to the jenkins_plugin module. Remote attackers could use this flaw to expose sensitive information from a remote host's logs. This flaw was fixed by not allowing passwords to be specified in the "params" argument, and noting this in the module documentation.

## References
- https://access.redhat.com/errata/RHSA-2017:2966
- https://bugzilla.redhat.com/show_bug.cgi?id=1473645
- https://github.com/ansible/ansible/issues/30874
