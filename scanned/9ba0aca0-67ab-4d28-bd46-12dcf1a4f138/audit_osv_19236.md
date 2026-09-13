# [H] CVE-2020-8933

## Summary
Severity: High
Advisory: CVE-2020-8933
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-22
Source: https://osv.dev/vulnerability/CVE-2020-8933
Type: osv

## Details
A vulnerability in Google Cloud Platform's guest-oslogin versions between 20190304 and 20200507 allows a user that is only granted the role "roles/compute.osLogin" to escalate privileges to root. Using the membership to the "lxd" group, an attacker can attach host devices and filesystems. Within an lxc container, it is possible to attach the host OS filesystem and modify /etc/sudoers to then gain administrative privileges. All images created after 2020-May-07 (20200507) are fixed, and if you cannot update, we recommend you edit /etc/group/security.conf and remove the "lxd" user from the OS Login entry.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00037.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00047.html
- https://cloud.google.com/support/bulletins/#gcp-2020-008
- https://github.com/GoogleCloudPlatform/guest-oslogin/pull/29
- https://gitlab.com/gitlab-com/gl-security/gl-redteam/red-team-tech-notes/-/tree/master/oslogin-privesc-june-2020
