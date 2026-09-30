# [H] CVE-2020-8907

## Summary
Severity: High
Advisory: CVE-2020-8907
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-22
Source: https://osv.dev/vulnerability/CVE-2020-8907
Type: osv

## Details
A vulnerability in Google Cloud Platform's guest-oslogin versions between 20190304 and 20200507 allows a user that is only granted the role "roles/compute.osLogin" to escalate privileges to root. Using their membership to the "docker" group, an attacker with this role is able to run docker and mount the host OS. Within docker, it is possible to modify the host OS filesystem and modify /etc/groups to gain administrative privileges. All images created after 2020-May-07 (20200507) are fixed, and if you cannot update, we recommend you edit /etc/group/security.conf and remove the "docker" user from the OS Login entry.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00037.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00047.html
- https://cloud.google.com/support/bulletins/#gcp-2020-008
- https://github.com/GoogleCloudPlatform/guest-oslogin/pull/29
- https://gitlab.com/gitlab-com/gl-security/gl-redteam/red-team-tech-notes/-/tree/master/oslogin-privesc-june-2020
