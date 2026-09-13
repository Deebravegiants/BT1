# [H] CVE-2023-24010

## Summary
Severity: High
Advisory: CVE-2023-24010
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:L)
Published: 2025-01-09
Source: https://osv.dev/vulnerability/CVE-2023-24010
Type: osv

## Details
An attacker can arbitrarily craft malicious DDS Participants (or ROS 2 Nodes) with valid certificates to compromise and get full control of the attacked secure DDS databus system by exploiting vulnerable attributes in the configuration of PKCS#7 certificate’s validation. This is caused by a non-compliant implementation of permission document verification used by some DDS vendors. Specifically, an improper use of the OpenSSL PKCS7_verify function used to validate S/MIME signatures.

## References
- https://gist.github.com/vmayoral/235c02d0b0ef85a29812eff6980ff80d
- https://github.com/ros2/sros2/issues/282
