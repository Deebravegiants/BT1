# [C] CVE-2015-9259

## Summary
Severity: Critical
Advisory: CVE-2015-9259
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-31
Source: https://osv.dev/vulnerability/CVE-2015-9259
Type: osv

## Details
In Docker Notary before 0.1, the checkRoot function in gotuf/client/client.go does not check expiry of root.json files, despite a comment stating that it does. Even if a user creates a new root.json file after a key compromise, an attacker can produce update files referring to an old root.json file.

## References
- https://docs.docker.com/notary/changelog/
- https://github.com/theupdateframework/notary/blob/master/docs/resources/ncc_docker_notary_audit_2015_07_31.pdf
