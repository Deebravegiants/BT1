# [C] CVE-2020-12443

## Summary
Severity: Critical
Advisory: CVE-2020-12443
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-29
Source: https://osv.dev/vulnerability/CVE-2020-12443
Type: osv

## Details
BigBlueButton before 2.2.6 allows remote attackers to read arbitrary files because the presfilename (lowercase) value can be a .pdf filename while the presFilename (mixed case) value has a ../ sequence. This can be leveraged for privilege escalation via a directory traversal to bigbluebutton.properties. NOTE: this issue exists because of an ineffective mitigation to CVE-2020-12112 in which there was an attempted fix within an NGINX configuration file, without considering that the relevant part of NGINX is case-insensitive.

## References
- https://github.com/bigbluebutton/bigbluebutton/pull/9259/commits/b21ca8355a57286a1e6df96984b3a4c57679a463
- https://github.com/mclab-hbrs/BBB-POC
