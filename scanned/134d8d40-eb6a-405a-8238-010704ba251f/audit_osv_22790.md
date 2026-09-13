# [C] CI/CD Docker Escape in OneDev

## Summary
Severity: Critical
Advisory: CVE-2022-39206
Aliases: GHSA-gjq9-4xx9-cr3q
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-09-13
Source: https://osv.dev/vulnerability/CVE-2022-39206
Type: osv

## Details
Onedev is an open source, self-hosted Git Server with CI/CD and Kanban. When using Docker-based job executors, the Docker socket (e.g. /var/run/docker.sock on Linux) is mounted into each Docker step. Users that can define and trigger CI/CD jobs on a project could use this to control the Docker daemon on the host machine. This is a known dangerous pattern, as it can be used to break out of Docker containers and, in most cases, gain root privileges on the host system. This issue allows regular (non-admin) users to potentially take over the build infrastructure of a OneDev instance. Attackers need to have an account (or be able to register one) and need permission to create a project. Since code.onedev.io has the right preconditions for this to be exploited by remote attackers, it could have been used to hijack builds of OneDev itself, e.g. by injecting malware into the docker images that are built and pushed to Docker Hub. The impact is increased by this as described before. Users are advised to upgrade to 7.3.0 or higher. There are no known workarounds for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39206.json
- https://github.com/theonedev/onedev/security/advisories/GHSA-gjq9-4xx9-cr3q
- https://nvd.nist.gov/vuln/detail/CVE-2022-39206
- https://github.com/theonedev/onedev/commit/0052047a5b5095ac6a6b4a73a522d0272fec3a22
- https://blog.sonarsource.com/onedev-remote-code-execution/
