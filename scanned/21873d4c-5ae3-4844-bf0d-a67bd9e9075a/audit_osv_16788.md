# [H] CVE-2019-9749

## Summary
Severity: High
Advisory: CVE-2019-9749
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-03-13
Source: https://osv.dev/vulnerability/CVE-2019-9749
Type: osv

## Details
An issue was discovered in the MQTT input plugin in Fluent Bit through 1.0.4. When this plugin acts as an MQTT broker (server), it mishandles incoming network messages. After processing a crafted packet, the plugin's mqtt_packet_drop function (in /plugins/in_mqtt/mqtt_prot.c) executes the memmove() function with a negative size parameter. That leads to a crash of the whole Fluent Bit server via a SIGSEGV signal.

## References
- https://github.com/fluent/fluent-bit/issues/1135
