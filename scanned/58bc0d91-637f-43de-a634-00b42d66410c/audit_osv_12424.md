# [H] CVE-2018-11789

## Summary
Severity: High
Advisory: CVE-2018-11789
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-03-21
Source: https://osv.dev/vulnerability/CVE-2018-11789
Type: osv

## Details
When accessing the heron-ui webpage, people can modify the file paths outside of the current container to access any file on the host. Example woule be modifying the parameter path= to go to the directory you would like to view. i.e. ..%2F..%2F..%2F..%2F..%2F..%2Fetc%2Fpasswd.

## References
- https://lists.apache.org/thread.html/5ea1a102d87a47c5912d745fa0d5dfa2830fc94099cbc30911f095b9%40%3Cdev.heron.apache.org%3E
- http://www.securityfocus.com/bid/107430
