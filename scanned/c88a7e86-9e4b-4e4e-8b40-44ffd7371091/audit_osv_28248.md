# [C] Microchip Harmony 3 Core library allows read and write access to RAM via a SCSI READ or WRITE command

## Summary
Severity: Critical
Advisory: CVE-2024-30212
CVSS: 9.0 (CVSS:4.0/AV:P/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2024-05-28
Source: https://osv.dev/vulnerability/CVE-2024-30212
Type: osv

## Details
If a SCSI READ(10) command is initiated via USB using the largest LBA 
(0xFFFFFFFF) with it's default block size of 512 and a count of 1,

the first 512 byte of the 0x80000000 memory area is returned to the 
user. If the block count is increased, the full RAM can be exposed.

The same method works to write to this memory area. If RAM contains 
pointers, those can be - depending on the application - overwritten to

return data from any other offset including Progam and Boot Flash.

## References
- https://github.com/Microchip-MPLAB-Harmony
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/30xxx/CVE-2024-30212.json
- https://github.com/Microchip-MPLAB-Harmony/core/blob/master/release_notes.md
- https://nvd.nist.gov/vuln/detail/CVE-2024-30212
- https://github.com/Microchip-MPLAB-Harmony/core/commit/d4608a4f1a140bd899cd4337cdbfb343a4339216
- https://github.com/Fehr-GmbH/blackleak
