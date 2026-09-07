# [M] Incorrect Default Permissions in CRI-O

## Summary
Severity: Medium
Advisory: GHSA-4hj2-r2pm-3hc6
CVE: CVE-2022-27652
CWE: CWE-276
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-04-22
Source: https://github.com/advisories/GHSA-4hj2-r2pm-3hc6
Type: github-advisory

## Affected
- Go: `github.com/cri-o/cri-o` — affected >=0 <1.24.0

## Details
### Impact

A bug was found in CRI-O where containers were incorrectly started with non-empty inheritable Linux process capabilities, creating an atypical Linux environment and enabling programs with inheritable file capabilities to elevate those capabilities to the permitted set during `execve(2)`.  Normally, when executable programs have specified permitted file capabilities, otherwise unprivileged users and processes can execute those programs and gain the specified file capabilities up to the bounding set.  Due to this bug, containers which included executable programs with inheritable file capabilities allowed otherwise unprivileged users and processes to additionally gain these inheritable file capabilities up to the container's bounding set.  Containers which use Linux users and groups to perform privilege separation inside the container are most directly impacted.

This bug did not affect the container security sandbox as the inheritable set never contained more capabilities than were included in the container's bounding set.


### Patches

This bug will been fixed in the following versions of CRI-O:
- v1.24.0

Users should update to the version corresponding to their minor release as soon as possible.  Running containers should be stopped, deleted, and recreated for the inheritable capabilities to be reset.

This fix changes CRI-O behavior such that containers are started with a more typical Linux environment.  Refer to `capabilities(7)` for a description of how capabilities work.  Note that permitted file capabilities continue to allow for privileges to be raised up to the container's bounding set and that processes may add capabilities to their own inheritable set up to the container's bounding set per the rules described in the manual page.  In all cases the container's bounding set provides an upper bound on the capabilities that can be assumed and provides for the container security sandbox.

### Workarounds

The entrypoint of a container can be modified to use a utility like `capsh(1)` to drop inheritable capabilities prior to the primary process starting.

### Credits

CRI-O would like to thank [Andrew G. Morgan](https://github.com/AndrewGMorgan) for responsibly disclosing this issue, as well as the Moby (Docker Engine) project for working with the other container engines in coordinating a fix.

### For more information

If you have any questions or comments about this advisory:

* [Open an issue](https://github.com/cri-o/cri-o/issues/new)
* Email us at [cncf-crio-security@lists.cncf.io](cncf-crio-security@lists.cncf.io) if you think you’ve found a security bug

------------------

https://www.first.org/cvss/calculator/3.1#CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L
4.8/Medium

|Metric	|Value	|Comments	|
|---	|---	|---	|
|Attack Vector (AV)	|Local	|An attacker requires local control to launch a container with files that have inheritable capabilities. 	|
|Attack Complexity (AC)	|Low	|Modifying a file to have inheritable capabilities is not difficult.	|
|Privileges Required (PR)	|Low	|An attacker requires enough privilege to cause a container to be launched with a compromised image.  Moby's API is typically bound to a local Unix domain socket and requires calls to be made from a process that is either UID 0 or present in the configured group.	|
|User Interaction (UI)	|Required	|An attacker must cause the compromised image to be run.	|
|Scope (S)	|Unchanged	|The container boundary set by Moby, including the bounding capability set, is not modified.  A successful attack gains access to privileges and resources within the boundary, not outside of it.	|
|Confidentiality (C)	|Low	|An attacker may gain access to some confidential information through elevation of CAP_CHOWN, CAP_DAC_OVERRIDE, CAP_FOWNER, CAP_SETFCAP, or CAP_SETPCAP, but the exposed information is limited to that which is already inside the container.	|
|Integrity (I)	|Low	|An attacker may be able to tamper with data inside the container through elevation of CAP_CHOWN, CAP_DAC_OVERRIDE, CAP_FOWNER, CAP_SETFCAP, or CAP_SETPCAP, or spoof packets with CAP_NET_RAW, but the tampered data is limited to that which is already inside the container.	|
|Availability (A)	|Low	|An attacker may be able to affect the availability of an application running inside the container through elevation of CAP_KILL or CAP_NET_RAW, or may be able to affect availability through tampering with file dependencies.	|

## References
- https://github.com/cri-o/cri-o/security/advisories/GHSA-4hj2-r2pm-3hc6
- https://nvd.nist.gov/vuln/detail/CVE-2022-27652
- https://bugzilla.redhat.com/show_bug.cgi?id=2066839
- https://github.com/cri-o/cri-o
