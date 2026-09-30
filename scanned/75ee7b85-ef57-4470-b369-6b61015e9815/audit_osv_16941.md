# [M] CVE-2020-10762

## Summary
Severity: Medium
Advisory: CVE-2020-10762
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-11-24
Source: https://osv.dev/vulnerability/CVE-2020-10762
Type: osv

## Details
An information-disclosure flaw was found in the way that gluster-block before 0.5.1 logs the output from gluster-block CLI operations. This includes recording passwords to the cmd_history.log file which is world-readable. This flaw allows local users to obtain sensitive information by reading the log file. The highest threat from this vulnerability is to data confidentiality.

## References
- https://github.com/gluster/gluster-block/releases/tag/v0.5.1
- https://bugzilla.redhat.com/show_bug.cgi?id=1845067
