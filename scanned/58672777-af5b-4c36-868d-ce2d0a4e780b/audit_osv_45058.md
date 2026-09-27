# [H] PYSEC-2024-119

## Summary
Severity: High
Advisory: PYSEC-2024-119
Aliases: CVE-2024-7807
Ecosystem: PyPI
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-29
Source: https://osv.dev/vulnerability/PYSEC-2024-119
Type: osv

## Affected
- PyPI: `chuanhuchatgpt` — affected >=0 <919222d285d73b9dcd71fb34de379eef8c90d175

## Details
A vulnerability in gaizhenbiao/chuanhuchatgpt version 20240628 allows for a Denial of Service (DOS) attack. When uploading a file, if an attacker appends a large number of characters to the end of a multipart boundary, the system will continuously process each character, rendering ChuanhuChatGPT inaccessible. This uncontrolled resource consumption can lead to prolonged unavailability of the service, disrupting operations and causing potential data inaccessibility and loss of productivity.

## References
- https://huntr.com/bounties/db67276d-36ee-4487-9165-b621c67ef8a3
- https://github.com/gaizhenbiao/chuanhuchatgpt/commit/919222d285d73b9dcd71fb34de379eef8c90d175
