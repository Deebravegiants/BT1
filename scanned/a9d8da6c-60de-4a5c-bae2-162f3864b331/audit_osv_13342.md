# [C] CVE-2018-19417

## Summary
Severity: Critical
Advisory: CVE-2018-19417
CVSS: 10.0 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2018-11-21
Source: https://osv.dev/vulnerability/CVE-2018-19417
Type: osv

## Details
An issue was discovered in the MQTT server in Contiki-NG before 4.2. The function parse_publish_vhdr() that parses MQTT PUBLISH messages with a variable length header uses memcpy to input data into a fixed size buffer. The allocated buffer can fit only MQTT_MAX_TOPIC_LENGTH (default 64) bytes, and a length check is missing. This could lead to Remote Code Execution via a stack-smashing attack (overwriting the function return address). Contiki-NG does not separate the MQTT server from other servers and the OS modules, so access to all memory regions is possible.

## References
- https://github.com/contiki-ng/contiki-ng/issues/600
