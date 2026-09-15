# [H] CVE-2021-33176

## Summary
Severity: High
Advisory: CVE-2021-33176
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-06-08
Source: https://osv.dev/vulnerability/CVE-2021-33176
Type: osv

## Details
VerneMQ MQTT Broker versions prior to 1.12.0 are vulnerable to a denial of service attack as a result of excessive memory consumption due to the handling of untrusted inputs. These inputs cause the message broker to consume large amounts of memory, resulting in the application being terminated by the operating system.

## References
- https://www.synopsys.com/blogs/software-security/cyrc-advisory-rabbitmq-emqx-vernemq
