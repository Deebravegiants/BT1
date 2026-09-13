# [M] CVE-2019-12825

## Summary
Severity: Medium
Advisory: CVE-2019-12825
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-02-17
Source: https://osv.dev/vulnerability/CVE-2019-12825
Type: osv

## Details
Unauthorized Access to the Container Registry of other groups was discovered in GitLab Enterprise 12.0.0-pre. In other words, authenticated remote attackers can read Docker registries of other groups. When a legitimate user changes the path of a group, Docker registries are not adapted, leaving them in the old namespace. They are not protected and are available to all other users with no previous access to the repo.

## References
- https://about.gitlab.com/blog/categories/releases/
- https://atomic111.github.io/article/gitlab-Unauthorized-Access-to-Container-Registry
