# [H] CVE-2018-14568

## Summary
Severity: High
Advisory: CVE-2018-14568
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-07-23
Source: https://osv.dev/vulnerability/CVE-2018-14568
Type: osv

## Details
Suricata before 4.0.5 stops TCP stream inspection upon a TCP RST from a server. This allows detection bypass because Windows TCP clients proceed with normal processing of TCP data that arrives shortly after an RST (i.e., they act as if the RST had not yet been received).

## References
- https://suricata-ids.org/2018/07/18/suricata-4-0-5-available/
- https://github.com/OISF/suricata/pull/3428/commits/843d0b7a10bb45627f94764a6c5d468a24143345
- https://github.com/kirillwow/ids_bypass
- https://redmine.openinfosecfoundation.org/issues/2501
