# [C] CVE-2018-1000831

## Summary
Severity: Critical
Advisory: CVE-2018-1000831
CVSS: 10.0 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2018-12-20
Source: https://osv.dev/vulnerability/CVE-2018-1000831
Type: osv

## Details
K9Mail version <= v5.600 contains a XML External Entity (XXE) vulnerability in WebDAV response parser that can result in Disclosure of confidential data, denial of service, SSRF, port scanning. This attack appear to be exploitable via malicious WebDAV server or intercept the reponse of a valid WebDAV server.

## References
- https://0dd.zone/2018/10/28/k9mail-XXE-MitM/
- https://github.com/k9mail/k-9/issues/3681
