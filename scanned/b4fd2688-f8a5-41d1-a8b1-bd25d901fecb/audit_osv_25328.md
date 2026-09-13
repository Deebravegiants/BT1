# [M] Spring AMQP Deserialization Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2023-34050
CVSS: 5.0 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:L/A:H)
Published: 2023-10-19
Source: https://osv.dev/vulnerability/CVE-2023-34050
Type: osv

## Details
In spring AMQP versions 1.0.0 to
2.4.16 and 3.0.0 to 3.0.9 , allowed list patterns for deserializable class
names were added to Spring AMQP, allowing users to lock down deserialization of
data in messages from untrusted sources; however by default, when no allowed
list was provided, all classes could be deserialized.



Specifically, an application is
vulnerable if




   *  the
     SimpleMessageConverter or SerializerMessageConverter is used

   *  the user
     does not configure allowed list patterns

   *  untrusted
     message originators gain permissions to write messages to the RabbitMQ
     broker to send malicious content

## References
- https://spring.io/security/cve-2023-34050
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/34xxx/CVE-2023-34050.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-34050
