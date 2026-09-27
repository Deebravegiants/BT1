# [M] LibOSDP RMAC revert to the beginning of the session

## Summary
Severity: Medium
Advisory: GHSA-xhjw-7vh5-qxqm
CVE: CVE-2024-52288
CWE: CWE-924
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-03-08
Source: https://github.com/advisories/GHSA-xhjw-7vh5-qxqm
Type: github-advisory

## Affected
- PyPI: `libosdp` — affected >=0 <3.0.0

## Details
- Issues:
  - SCS_14 is allowed on encrypted connection (osdp_phy.c)
  - No validation for RMAC_I is only in response to osdp_SCRYPT (osdp_cp.c)
  - Couldn't find anything specific in the OSDP specifications indicating it is forbidden, I'm gussing it shouldn't be allowed according from the secure connection initialization flow (let me know if you think there is spec-rela
ted change that should be done)
- Attack:
  - Once RMAC_I message can be sent during a session, attacker with MITM access to the communication may intercept the original RMAC_I reply and save it.
  - While the session continues, the attacker will record all of the replies and save them, till capturing the message to be replied (can be detected by ID, length or time based on inspection of visual activity next to the reade
r)
  - Once attacker captures a session with the message to be replayed, he stops reseting the connection and waits for signal to perform the replay to of the PD to CP message (ex: by signaling remotly to the MIMT device or setting
 a specific timing).
  - in order to replay, the attacker will craft a specific RMAC_I message in the proper seq of the execution, which will result in reverting the RMAC to the begining of the session.
  - At that phase - attacker can replay all the messages from the begining of the session.

### Impact
Replay attack

### Patches
This issue has been fixed in 298576d9214b48214092eebdd892ec77be085e5a

## References
- https://github.com/goToMain/libosdp/security/advisories/GHSA-xhjw-7vh5-qxqm
- https://nvd.nist.gov/vuln/detail/CVE-2024-52288
- https://github.com/goToMain/libosdp/commit/298576d9214b48214092eebdd892ec77be085e5a
- https://github.com/goToMain/libosdp
