# [H] CVE-2023-4235

## Summary
Severity: High
Advisory: CVE-2023-4235
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2023-4235
Type: osv

## Details
A flaw was found in ofono, an Open Source Telephony on Linux. A stack overflow bug is triggered within the decode_deliver_report() function during the SMS decoding. It is assumed that the attack scenario is accessible from a compromised modem, a malicious base station, or just SMS. There is a bound check for this memcpy length in decode_submit(), but it was forgotten in decode_deliver_report().

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RLAWJAAS3HDI2KMCZXF4DMR3Y4BQNMKO/
- https://bugzilla.redhat.com/show_bug.cgi?id=2255402
