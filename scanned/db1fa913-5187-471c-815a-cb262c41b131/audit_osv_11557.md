# [M] CVE-2017-8443

## Summary
Severity: Medium
Advisory: CVE-2017-8443
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2017-06-30
Source: https://osv.dev/vulnerability/CVE-2017-8443
Type: osv

## Details
In Kibana X-Pack security versions prior to 5.4.3 if a Kibana user opens a crafted Kibana URL the result could be a redirect to an improperly initialized Kibana login screen. If the user enters credentials on this screen, the credentials will appear in the URL bar. The credentials could then be viewed by untrusted parties or logged into the Kibana access logs.

## References
- https://www.elastic.co/community/security
