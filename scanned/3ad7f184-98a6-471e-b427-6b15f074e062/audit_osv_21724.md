# [M] CVE-2021-45936

## Summary
Severity: Medium
Advisory: CVE-2021-45936
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-01
Source: https://osv.dev/vulnerability/CVE-2021-45936
Type: osv

## Details
wolfSSL wolfMQTT 1.9 has a heap-based buffer overflow in MqttDecode_Disconnect (called from MqttClient_DecodePacket and MqttClient_WaitType).

## References
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=39053
- https://github.com/wolfSSL/wolfMQTT/commit/84d4b53122e0fa0280c7872350b89d5777dabbb2
- https://github.com/google/oss-fuzz-vulns/blob/main/vulns/wolfmqtt/OSV-2021-1348.yaml
