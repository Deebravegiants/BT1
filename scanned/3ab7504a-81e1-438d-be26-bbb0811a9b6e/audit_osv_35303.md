# [H] CVE-2025-70954

## Summary
Severity: High
Advisory: CVE-2025-70954
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-02-13
Source: https://osv.dev/vulnerability/CVE-2025-70954
Type: osv

## Details
A Null Pointer Dereference vulnerability exists in the TON Virtual Machine (TVM) within the TON Blockchain before v2025.06. The issue is located in the execution logic of the INMSGPARAM instruction, where the program fails to validate if a specific pointer is null before accessing it. By sending a malicious transaction or smart contract, an attacker can trigger this null pointer dereference, causing the validator node process to crash (segmentation fault). This results in a Denial of Service (DoS) affecting the availability of the entire blockchain network.

## References
- https://gist.github.com/Lucian-code233/04940a264cab50732cc07fd991749226
- https://github.com/ton-blockchain/ton/releases/tag/v2025.06#:~:text=AArayz%2C%20wy666444%2C%20Robinlzw%2C%20Lucian-code233
- https://mp.weixin.qq.com/s/IbRKrCKdMyIi-azkuqOOvg
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/70xxx/CVE-2025-70954.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-70954
- https://github.com/ton-blockchain/ton/commit/9e5109d56bc4f2345a00b2271c3711103841b799
- https://www.tonbit.xyz/blog/post/TonBit-Discovers-Critical-Vulnerability-on-TON-Virtual-Machine-for-the-Third-Time-Once-Again-Receiving-Official-Recognition-from-the-TON-Team.html
