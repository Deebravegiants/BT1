# [M] CVE-2019-10045

## Summary
Severity: Medium
Advisory: CVE-2019-10045
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2019-05-31
Source: https://osv.dev/vulnerability/CVE-2019-10045
Type: osv

## Details
The "action" get_sess_id in the web application of Pydio through 8.2.2 discloses the session cookie value in the response body, enabling scripts to get access to its value. This identifier can be reused by an attacker to impersonate a user and perform actions on behalf of him/her (if the session is still active).

## References
- https://www.secureauth.com/labs/advisories
