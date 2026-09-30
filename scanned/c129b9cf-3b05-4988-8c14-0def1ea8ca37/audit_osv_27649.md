# [H] CVE-2024-24478

## Summary
Severity: High
Advisory: CVE-2024-24478
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-21
Source: https://osv.dev/vulnerability/CVE-2024-24478
Type: osv

## Details
An issue in Wireshark before 4.2.0 allows a remote attacker to cause a denial of service via the packet-bgp.c, dissect_bgp_open(tvbuff_t*tvb, proto_tree*tree, packet_info*pinfo), optlen components. NOTE: this is disputed by the vendor because neither release 4.2.0 nor any other release was affected.

## References
- https://gist.github.com/1047524396/e82c55147cd3cb62ef20cbdb0ec83694
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24478.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-24478
- https://gitlab.com/wireshark/wireshark/-/issues/19347
- https://github.com/wireshark/wireshark/commit/80a4dc55f4d2fa33c2b36a99406500726d3faaef
