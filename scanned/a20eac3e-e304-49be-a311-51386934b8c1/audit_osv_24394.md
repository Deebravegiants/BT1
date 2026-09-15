# [C] CVE-2023-1523

## Summary
Severity: Critical
Advisory: CVE-2023-1523
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-09-01
Source: https://osv.dev/vulnerability/CVE-2023-1523
Type: osv

## Details
Using the TIOCLINUX ioctl request, a malicious snap could inject contents into the input of the controlling terminal which could allow it to cause arbitrary commands to be executed outside of the snap sandbox after the snap exits. Graphical terminal emulators like xterm, gnome-terminal and others are not affected - this can only be exploited when snaps are run on a virtual console.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/1xxx/CVE-2023-1523.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-1523
- https://ubuntu.com/security/notices/USN-6125-1
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2023-1523
- https://github.com/snapcore/snapd/pull/12849
- https://github.com/snapcore/snapd
- https://github.com/snapcore/snapd/releases
- https://marc.info/?l=oss-security&m=167879021709955&w=2
