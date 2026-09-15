# [C] CVE-2018-11757

## Summary
Severity: Critical
Advisory: CVE-2018-11757
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-23
Source: https://osv.dev/vulnerability/CVE-2018-11757
Type: osv

## Details
In Docker Skeleton Runtime for Apache OpenWhisk, a Docker action inheriting the Docker tag openwhisk/dockerskeleton:1.3.0 (or earlier) may allow an attacker to replace the user function inside the container if the user code is vulnerable to code exploitation.

## References
- https://lists.apache.org/thread.html/0b6d8a677f1c063ed32eb3638ef4d1a47dfba8907de4b222ddd24b05%40%3Cdev.openwhisk.apache.org%3E
- http://www.securityfocus.com/bid/104913
- https://www.puresec.io/hubfs/Apache%20OpenWhisk%20PureSec%20Security%20Advisory.pdf
- https://github.com/apache/incubator-openwhisk-runtime-docker/commit/891896f25c39bc336ef6dda53f80f466ac4ca3c8
