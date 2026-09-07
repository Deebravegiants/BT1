# [M] Docker supplementary group permissions not set up properly, allowing attackers to bypass primary group restrictions

## Summary
Severity: Medium
Advisory: GHSA-rc4r-wh2q-q6c4
CVE: CVE-2022-36109
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-rc4r-wh2q-q6c4
Type: github-advisory

## Affected
- Go: `github.com/docker/docker` — affected >=0 <20.10.18

## Details
Moby is an open-source project created by Docker to enable software containerization. A bug was found in Moby (Docker Engine) where supplementary groups are not set up properly. If an attacker has direct access to a container and manipulates their supplementary group access, they may be able to use supplementary group access to bypass primary group restrictions in some cases, potentially gaining access to sensitive information or gaining the ability to execute code in that container.  This bug is fixed in Moby (Docker Engine) 20.10.18. Users should update to this version when it is available. Running containers should be stopped and restarted for the permissions to be fixed. For users unable to upgrade, this problem can be worked around by not using the `"USER $USERNAME"` Dockerfile instruction. Instead by calling `ENTRYPOINT ["su", "-", "user"]` the supplementary groups will be set up properly.

Thanks to Steven Murdoch for reporting this issue.

----

### Impact

If an attacker has direct access to a container and manipulates their supplementary group access, they may be able to use supplementary group access to bypass primary group restrictions in some cases, potentially gaining access to sensitive information or gaining the ability to execute code in that container. 

### Patches

 This bug is fixed in Moby (Docker Engine) 20.10.18. Users should update to this version when it is available.

### Workarounds

This problem can be worked around by not using the `"USER $USERNAME"` Dockerfile instruction. Instead by calling `ENTRYPOINT ["su", "-", "user"]` the supplementary groups will be set up properly.

### References

https://www.benthamsgaze.org/2022/08/22/vulnerability-in-linux-containers-investigation-and-mitigation/

### For more information

If you have any questions or comments about this advisory:

* [Open an issue](https://github.com/moby/moby/issues/new)
* Email us at [security@docker.com](mailto:security@docker.com)

## References
- https://github.com/moby/moby/security/advisories/GHSA-rc4r-wh2q-q6c4
- https://nvd.nist.gov/vuln/detail/CVE-2022-36109
- https://github.com/moby/moby/commit/de7af816e76a7fd3fbf06bffa6832959289fba32
- https://github.com/moby/moby
- https://github.com/moby/moby/releases/tag/v20.10.18
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/O7JL2QA3RB732MLJ3RMUXB3IB7AA22YU
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RQQ4E3JBXVR3VK5FIZVJ3QS2TAOOXXTQ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/O7JL2QA3RB732MLJ3RMUXB3IB7AA22YU
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RQQ4E3JBXVR3VK5FIZVJ3QS2TAOOXXTQ
- https://www.benthamsgaze.org/2022/08/22/vulnerability-in-linux-containers-investigation-and-mitigation
