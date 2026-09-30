# [M] CVE-2021-22097

## Summary
Severity: Medium
Advisory: CVE-2021-22097
Aliases: GHSA-fx7f-rjqj-52pj
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-10-28
Source: https://osv.dev/vulnerability/CVE-2021-22097
Type: osv

## Details
In Spring AMQP versions 2.2.0 - 2.2.18 and 2.3.0 - 2.3.10, the Spring AMQP Message object, in its toString() method, will deserialize a body for a message with content type application/x-java-serialized-object. It is possible to construct a malicious java.util.Dictionary object that can cause 100% CPU usage in the application if the toString() method is called.

## References
- https://tanzu.vmware.com/security/cve-2021-22097
