# [M] CVE-2021-3681

## Summary
Severity: Medium
Advisory: CVE-2021-3681
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-04-18
Source: https://osv.dev/vulnerability/CVE-2021-3681
Type: osv

## Details
A flaw was found in Ansible Galaxy Collections. When collections are built manually, any files in the repository directory that are not explicitly excluded via the ``build_ignore`` list in "galaxy.yml" include files in the ``.tar.gz`` file. This contains sensitive info, such as the user's Ansible Galaxy API key and any secrets in ``ansible`` or ``ansible-playbook`` verbose output without the``no_log`` redaction. Currently, there is no way to deprecate a Collection Or delete a Collection Version. Once published, anyone who downloads or installs the collection can view the secrets.

## References
- https://github.com/ansible/galaxy/issues/1977
- https://bugzilla.redhat.com/show_bug.cgi?id=1989407
