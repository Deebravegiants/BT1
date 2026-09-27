# [H] CVE-2019-15701

## Summary
Severity: High
Advisory: CVE-2019-15701
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-08-27
Source: https://osv.dev/vulnerability/CVE-2019-15701
Type: osv

## Details
components/Modals/HelpModal.jsx in BloodHound 2.2.0 allows remote attackers to execute arbitrary OS commands (by spawning a child process as the current user on the victim's machine) when the search function's autocomplete feature is used. The victim must import data from an Active Directory with a GPO containing JavaScript in its name.

## References
- https://github.com/BloodHoundAD/BloodHound/issues/267
