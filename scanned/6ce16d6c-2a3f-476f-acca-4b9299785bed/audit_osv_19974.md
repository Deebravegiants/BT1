# [H] CVE-2021-28848

## Summary
Severity: High
Advisory: CVE-2021-28848
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-06-03
Source: https://osv.dev/vulnerability/CVE-2021-28848
Type: osv

## Details
Mintty before 3.4.5 allows remote servers to cause a denial of service (Windows GUI hang) by telling the Mintty window to change its title repeatedly at high speed, which results in many SetWindowTextA or SetWindowTextW calls. In other words, it does not implement a usleep or similar delay upon processing a title change.

## References
- https://mintty.github.io/
- https://github.com/mintty/mintty/commit/bd52109993440b6996760aaccb66e68e782762b9
- https://github.com/mintty/mintty/compare/3.4.4...3.4.5
