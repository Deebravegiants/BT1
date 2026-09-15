# [M] CVE-2020-10701

## Summary
Severity: Medium
Advisory: CVE-2020-10701
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-27
Source: https://osv.dev/vulnerability/CVE-2020-10701
Type: osv

## Details
A missing authorization flaw was found in the libvirt API responsible for changing the QEMU agent response timeout. This flaw allows read-only connections to adjust the time that libvirt waits for the QEMU guest agent to respond to agent commands. Depending on the timeout value that is set, this flaw can make guest agent commands fail because the agent cannot respond in time. Unprivileged users with a read-only connection could abuse this flaw to set the response timeout for all guest agent messages to zero, potentially leading to a denial of service. This flaw affects libvirt versions before 6.2.0.

## References
- https://security.netapp.com/advisory/ntap-20210708-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=1819163
