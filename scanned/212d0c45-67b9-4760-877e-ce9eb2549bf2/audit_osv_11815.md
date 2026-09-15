# [M] CVE-2017-9868

## Summary
Severity: Medium
Advisory: CVE-2017-9868
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-06-25
Source: https://osv.dev/vulnerability/CVE-2017-9868
Type: osv

## Details
In Mosquitto through 1.4.12, mosquitto.db (aka the persistence file) is world readable, which allows local users to obtain sensitive MQTT topic information.

## References
- https://lists.debian.org/debian-lts-announce/2018/09/msg00036.html
- https://github.com/eclipse/mosquitto/issues/468
