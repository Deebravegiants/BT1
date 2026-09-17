# [M] CVE-2021-26917

## Summary
Severity: Medium
Advisory: CVE-2021-26917
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-02-08
Source: https://osv.dev/vulnerability/CVE-2021-26917
Type: osv

## Details
PyBitmessage through 0.6.3.2 allows attackers to write screen captures to Potentially Unwanted Directories via a crafted apinotifypath value. NOTE: the discoverer states "security mitigation may not be necessary as there is no evidence yet that these screen intercepts are actually transported away from the local host." NOTE: it is unclear whether there are any common use cases in which apinotifypath is controlled by an attacker

## References
- https://attack.mitre.org/techniques/T1113/
- https://github.com/Bitmessage/PyBitmessage/releases
- https://github.com/Bitmessage/PyBitmessage/blob/f381721bec31641002e2f240309600c4994855a7/src/api.py#L35-L37
- https://poal.co/s/technology/290479
