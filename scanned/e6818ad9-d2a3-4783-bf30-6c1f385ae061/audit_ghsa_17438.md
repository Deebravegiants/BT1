# [M] Eclipse Paho Go MQTT may incorrectly encode strings if length exceeds 65535 bytes

## Summary
Severity: Medium
Advisory: GHSA-32fw-gq77-f2f2
CVE: CVE-2025-10543
CWE: CWE-197
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-02
Source: https://github.com/advisories/GHSA-32fw-gq77-f2f2
Type: github-advisory

## Affected
- Go: `github.com/eclipse/paho.mqtt.golang` — affected >=0 <1.5.1

## Details
In Eclipse Paho Go MQTT v3.1 library (paho.mqtt.golang) versions <=1.5.0 UTF-8 encoded strings, passed into the library, may be incorrectly encoded if their length exceeds 65535 bytes. This may lead to unexpected content in packets sent to the server (for example, part of an MQTT topic may leak into the message body in a PUBLISH packet).

The issue arises because the length of the data passed in was converted from an int64/int32 (depending upon CPU) to an int16 without checks for overflows. The int16 length was then written, followed by the data (e.g. topic). This meant that when the data (e.g. topic) was over 65535 bytes then the amount of data written exceeds what the length field indicates. This could lead to a corrupt packet, or mean that the excess data leaks into another field (e.g. topic leaks into message body).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-10543
- https://github.com/eclipse-paho/paho.mqtt.golang/issues/730
- https://github.com/eclipse-paho/paho.mqtt.golang/pull/714
- https://github.com/alpinelinux/build-server-status/commit/e3487897db32c8c3d0287643f8384a6669e93731
- https://github.com/advisories/GHSA-32fw-gq77-f2f2
- https://github.com/eclipse-paho/paho.mqtt.golang
- https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/254
