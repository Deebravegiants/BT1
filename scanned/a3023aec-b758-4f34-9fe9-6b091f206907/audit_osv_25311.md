# [H] CVE-2023-33658

## Summary
Severity: High
Advisory: CVE-2023-33658
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-06-08
Source: https://osv.dev/vulnerability/CVE-2023-33658
Type: osv

## Details
A heap buffer overflow vulnerability exists in NanoMQ 0.17.2. The vulnerability can be triggered by calling the function nni_msg_get_pub_pid() in the file message.c. An attacker could exploit this vulnerability to cause a denial of service attack.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/33xxx/CVE-2023-33658.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-33658
- https://github.com/emqx/nanomq/issues/1153
- https://github.com/nanomq/NanoNNG/commit/657e6c81c474bdee0e6413483b990e90610030c1
- https://github.com/emqx/nanomq
