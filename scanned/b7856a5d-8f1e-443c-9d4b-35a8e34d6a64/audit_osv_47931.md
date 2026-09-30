# [M] CVE-2017-15116

## Summary
Severity: Medium
Advisory: CVE-2017-15116
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-11-30
Source: https://osv.dev/vulnerability/CVE-2017-15116
Type: osv

## Details
The rngapi_reset function in crypto/rng.c in the Linux kernel before 4.2 allows attackers to cause a denial of service (NULL pointer dereference).

## References
- https://access.redhat.com/errata/RHSA-2018:0676
- https://access.redhat.com/errata/RHSA-2018:1062
- https://bugzilla.redhat.com/show_bug.cgi?id=1485815
- https://bugzilla.redhat.com/show_bug.cgi?id=1514609
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=94f1bb15bed84ad6c893916b7e7b9db6f1d7eec6
- https://github.com/torvalds/linux/commit/94f1bb15bed84ad6c893916b7e7b9db6f1d7eec6
