# [M] CVE-2017-7589

## Summary
Severity: Medium
Advisory: CVE-2017-7589
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-04-09
Source: https://osv.dev/vulnerability/CVE-2017-7589
Type: osv

## Details
In OpenIDM through 4.0.0 before 4.5.0, the info endpoint may leak sensitive information upon a request by the "anonymous" user, as demonstrated by responses with a 200 HTTP status code and a JSON object containing IP address strings. This is related to a missing access-control check in bin/defaults/script/info/login.js.

## References
- https://backstage.forgerock.com/knowledge/kb/article/a92936505
- http://www.rootlabs.com.br/information-disclosure-forgerock-openidm-4-0-0-and-4-5-0/
