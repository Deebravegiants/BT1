# [C] CVE-2021-20236

## Summary
Severity: Critical
Advisory: CVE-2021-20236
Aliases: GHSA-qq65-x72m-9wr8
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-28
Source: https://osv.dev/vulnerability/CVE-2021-20236
Type: osv

## Details
A flaw was found in the ZeroMQ server in versions before 4.3.3. This flaw allows a malicious client to cause a stack buffer overflow on the server by sending crafted topic subscription requests and then unsubscribing. The highest threat from this vulnerability is to confidentiality, integrity, as well as system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1921976
- https://github.com/zeromq/libzmq/security/advisories/GHSA-qq65-x72m-9wr8
