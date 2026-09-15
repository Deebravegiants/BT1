# [C] CVE-2018-11779

## Summary
Severity: Critical
Advisory: CVE-2018-11779
Aliases: GHSA-25pc-85qf-6j69
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-26
Source: https://osv.dev/vulnerability/CVE-2018-11779
Type: osv

## Details
In Apache Storm versions 1.1.0 to 1.2.2, when the user is using the storm-kafka-client or storm-kafka modules, it is possible to cause the Storm UI daemon to deserialize user provided bytes into a Java class.

## References
- https://lists.apache.org/thread.html/3e4f704c4bd9296405a07a0290b8cbb6cbf5046e277efe6d93280a98%40%3Cuser.storm.apache.org%3E
