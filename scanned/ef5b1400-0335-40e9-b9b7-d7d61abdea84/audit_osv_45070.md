# [C] PYSEC-2025-21

## Summary
Severity: Critical
Advisory: PYSEC-2025-21
Aliases: CVE-2025-1945, GHSA-w8jq-xcqf-f792
Ecosystem: PyPI
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-10
Source: https://osv.dev/vulnerability/PYSEC-2025-21
Type: osv

## Affected
- PyPI: `picklescan` — affected >=0 <e58e45e0d9e091159c1554f9b04828bbb40b9781, >=0 <0.0.23

## Details
picklescan before 0.0.23 fails to detect malicious pickle files inside PyTorch model archives when certain ZIP file flag bits are modified. By flipping specific bits in the ZIP file headers, an attacker can embed malicious pickle files that remain undetected by PickleScan while still being successfully loaded by PyTorch's torch.load(). This can lead to arbitrary code execution when loading a compromised model.

## References
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-w8jq-xcqf-f792
- https://sites.google.com/sonatype.com/vulnerabilities/cve-2025-1945
- https://github.com/mmaitre314/picklescan/commit/e58e45e0d9e091159c1554f9b04828bbb40b9781
