# [H] CVE-2020-27220

## Summary
Severity: High
Advisory: CVE-2020-27220
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-14
Source: https://osv.dev/vulnerability/CVE-2020-27220
Type: osv

## Details
The Eclipse Hono AMQP and MQTT protocol adapters do not check whether an authenticated gateway device is authorized to receive command & control messages when it has subscribed only to commands for a specific device. The missing check involves verifying that the command target device is configured giving permission for the gateway device to act on its behalf. This means an authenticated device of a certain tenant, notably also a non-gateway device acting like a gateway, may receive command & control messages targeted at a different device of the same tenant without corresponding permissions getting checked.

## References
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=569856
