# [H] CVE-2023-4233

## Summary
Severity: High
Advisory: CVE-2023-4233
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2023-4233
Type: osv

## Details
A flaw was found in ofono, an Open Source Telephony on Linux. A stack overflow bug is triggered within the sms_decode_address_field() function during the SMS PDU decoding. It is assumed that the attack scenario is accessible from a compromised modem, a malicious base station, or just SMS.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VG6FHQITWUNHBDGPXUQ77SZK5O5BYIBZ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NBTPKR3LYTTLROPXF77FL4SPLXVHNC4T/
- https://bugzilla.redhat.com/show_bug.cgi?id=2255396
