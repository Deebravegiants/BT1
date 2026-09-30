# [H] CVE-2021-40110

## Summary
Severity: High
Advisory: CVE-2021-40110
Aliases: GHSA-r58x-wjg8-63m9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-01-04
Source: https://osv.dev/vulnerability/CVE-2021-40110
Type: osv

## Details
In Apache James, using Jazzer fuzzer, we identified that an IMAP user can craft IMAP LIST commands to orchestrate a Denial Of Service using a vulnerable Regular expression. This affected Apache James prior to 3.6.1 We recommend upgrading to Apache James 3.6.1 or higher , which enforce the use of RE2J regular expression engine to execute regex in linear time without back-tracking.

## References
- http://www.openwall.com/lists/oss-security/2022/01/04/2
- https://www.openwall.com/lists/oss-security/2022/01/04/2
