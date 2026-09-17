# [M] CVE-2021-3155

## Summary
Severity: Medium
Advisory: CVE-2021-3155
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-02-17
Source: https://osv.dev/vulnerability/CVE-2021-3155
Type: osv

## Details
snapd 2.54.2 and earlier created ~/snap directories in user home directories without specifying owner-only permissions. This could allow a local attacker to read information that should have been private. Fixed in snapd versions 2.54.3+18.04, 2.54.3+20.04 and 2.54.3+21.10.1

## References
- https://github.com/snapcore/snapd/commit/6bcaeeccd16ed8298a301dd92f6907f88c24cc85
- https://github.com/snapcore/snapd/commit/7d2a966620002149891446a53cf114804808dcca
- https://ubuntu.com/security/notices/USN-5292-1
