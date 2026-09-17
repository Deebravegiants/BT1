# [H] CVE-2016-4989

## Summary
Severity: High
Advisory: CVE-2016-4989
CVSS: 7.0 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-11
Source: https://osv.dev/vulnerability/CVE-2016-4989
Type: osv

## Details
setroubleshoot allows local users to bypass an intended container protection mechanism and execute arbitrary commands by (1) triggering an SELinux denial with a crafted file name, which is handled by the _set_tpath function in audit_data.py or via a crafted (2) local_id or (3) analysis_id field in a crafted XML document to the run_fix function in SetroubleshootFixit.py, related to the subprocess.check_output and commands.getstatusoutput functions, a different vulnerability than CVE-2016-4445.

## References
- http://seclists.org/oss-sec/2016/q2/574
- https://access.redhat.com/errata/RHSA-2016:1293
- https://rhn.redhat.com/errata/RHSA-2016-1267.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1346461
- http://securitytracker.com/id/1036144
- https://github.com/fedora-selinux/setroubleshoot/commit/dda55aa50db95a25f0d919c3a0d5871827cdc40f
- https://github.com/fedora-selinux/setroubleshoot/commit/e69378d7e82a503534d29c5939fa219341e8f2ad
