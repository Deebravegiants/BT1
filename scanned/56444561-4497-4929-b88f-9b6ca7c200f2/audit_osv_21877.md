# [H] CVE-2022-0847

## Summary
Severity: High
Advisory: CVE-2022-0847
Aliases: A-220741611, ASB-A-220741611
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-10
Source: https://osv.dev/vulnerability/CVE-2022-0847
Type: osv

## Details
A flaw was found in the way the "flags" member of the new pipe buffer structure was lacking proper initialization in copy_page_to_iter_pipe and push_pipe functions in the Linux kernel and could thus contain stale values. An unprivileged local user could use this flaw to write to pages in the page cache backed by read only files and as such escalate their privileges on the system.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2022-0847
- http://packetstormsecurity.com/files/176534/Linux-4.20-KTLS-Read-Only-Write.html
- https://psirt.global.sonicwall.com/vuln-detail/SNWLID-2022-0015
- https://security.netapp.com/advisory/ntap-20220325-0005/
- https://cert-portal.siemens.com/productcert/pdf/ssa-222547.pdf
- https://www.suse.com/support/kb/doc/?id=000020603
- https://bugzilla.redhat.com/show_bug.cgi?id=2060795
- http://packetstormsecurity.com/files/166229/Dirty-Pipe-Linux-Privilege-Escalation.html
- https://dirtypipe.cm4all.com/
- http://packetstormsecurity.com/files/166230/Dirty-Pipe-SUID-Binary-Hijack-Privilege-Escalation.html
- http://packetstormsecurity.com/files/166258/Dirty-Pipe-Local-Privilege-Escalation.html
