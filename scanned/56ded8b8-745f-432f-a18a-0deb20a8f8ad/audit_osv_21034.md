# [H] CVE-2021-39947

## Summary
Severity: High
Advisory: CVE-2021-39947
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2022-06-06
Source: https://osv.dev/vulnerability/CVE-2021-39947
Type: osv

## Details
In specific circumstances, trace file buffers in GitLab Runner versions up to 14.3.4, 14.4 to 14.4.2, and 14.5 to 14.5.2 would re-use the file descriptor 0 for multiple traces and mix the output of several jobs

## References
- https://gitlab.com/gitlab-org/gitlab-runner/-/issues/28732
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39947.json
