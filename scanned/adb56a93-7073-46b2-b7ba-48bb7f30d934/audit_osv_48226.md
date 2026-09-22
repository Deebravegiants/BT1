# [M] CVE-2017-3157

## Summary
Severity: Medium
Advisory: CVE-2017-3157
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2017-11-20
Source: https://osv.dev/vulnerability/CVE-2017-3157
Type: osv

## Details
By exploiting the way Apache OpenOffice before 4.1.4 renders embedded objects, an attacker could craft a document that allows reading in a file from the user's filesystem. Information could be retrieved by the attacker by, e.g., using hidden sections to store the information, tricking the user into saving the document and convincing the user to send the document back to the attacker. The vulnerability is mitigated by the need for the attacker to know the precise file path in the target system, and the need to trick the user into saving the document and sending it back.

## References
- http://www.securityfocus.com/bid/96402
- https://access.redhat.com/errata/RHSA-2017:0914
- https://access.redhat.com/errata/RHSA-2017:0979
- http://www.securitytracker.com/id/1037893
- https://www.debian.org/security/2017/dsa-3792
- https://www.openoffice.org/security/cves/CVE-2017-3157.html
