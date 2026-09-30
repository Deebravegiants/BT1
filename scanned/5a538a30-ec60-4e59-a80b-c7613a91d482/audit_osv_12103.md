# [C] CVE-2018-10244

## Summary
Severity: Critical
Advisory: CVE-2018-10244
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-04
Source: https://osv.dev/vulnerability/CVE-2018-10244
Type: osv

## Details
Suricata version 4.0.4 incorrectly handles the parsing of an EtherNet/IP PDU. A malformed PDU can cause the parsing code to read beyond the allocated data because DecodeENIPPDU in app-layer-enip-commmon.c has an integer overflow during a length check.

## References
- https://suricata-ids.org/2018/07/18/suricata-4-0-5-available/
