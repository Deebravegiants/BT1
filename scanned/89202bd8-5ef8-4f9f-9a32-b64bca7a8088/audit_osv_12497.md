# [M] CVE-2018-12546

## Summary
Severity: Medium
Advisory: CVE-2018-12546
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-03-27
Source: https://osv.dev/vulnerability/CVE-2018-12546
Type: osv

## Details
In Eclipse Mosquitto version 1.0 to 1.5.5 (inclusive) when a client publishes a retained message to a topic, then has its access to that topic revoked, the retained message will still be published to clients that subscribe to that topic in the future. In some applications this may result in clients being able cause effects that would otherwise not be allowed.

## References
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=543127
