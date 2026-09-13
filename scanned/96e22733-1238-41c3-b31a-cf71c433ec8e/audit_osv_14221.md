# [M] CVE-2018-8023

## Summary
Severity: Medium
Advisory: CVE-2018-8023
Aliases: GHSA-c8cc-p3j7-4c7f
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-09-21
Source: https://osv.dev/vulnerability/CVE-2018-8023
Type: osv

## Details
Apache Mesos can be configured to require authentication to call the Executor HTTP API using JSON Web Token (JWT). In Apache Mesos versions pre-1.4.2, 1.5.0, 1.5.1, 1.6.0 the comparison of the generated HMAC value against the provided signature in the JWT implementation used is vulnerable to a timing attack because instead of a constant-time string comparison routine a standard `==` operator has been used. A malicious actor can therefore abuse the timing difference of when the JWT validation function returns to reveal the correct HMAC value.

## References
- https://lists.apache.org/thread.html/9b9d3f6bd09f3ebd2284b82077033bdc71da550a1c4c010c2494acc3%40%3Cdev.mesos.apache.org%3E
- https://lists.apache.org/thread.html/r0dd7ff197b2e3bdd80a0326587ca3d0c22e10d1dba17c769d6da7d7a%40%3Cuser.flink.apache.org%3E
