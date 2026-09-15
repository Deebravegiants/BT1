# [H] CVE-2018-12907

## Summary
Severity: High
Advisory: CVE-2018-12907
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-06-27
Source: https://osv.dev/vulnerability/CVE-2018-12907
Type: osv

## Details
In Rclone 1.42, use of "rclone sync" to migrate data between two Google Cloud Storage buckets might allow attackers to trigger the transmission of any URL's content to Google, because there is no validation of a URL field received from the Google Cloud Storage API server, aka a "RESTLESS" issue.

## References
- http://openwall.com/lists/oss-security/2018/06/27/3
- https://www.danieldent.com/blog/restless-vulnerability-non-browser-cross-domain-http-request-attacks/
