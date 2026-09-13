# [M] Apache ZooKeeper: Insufficient Permission Check in AdminServer Snapshot/Restore Commands

## Summary
Severity: Medium
Advisory: GHSA-2hmj-97jw-28jh
CVE: CVE-2025-58457
CWE: CWE-280
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-09-24
Source: https://github.com/advisories/GHSA-2hmj-97jw-28jh
Type: github-advisory

## Affected
- Maven: `org.apache.zookeeper:zookeeper` — affected >=3.9.0 <3.9.4

## Details
Improper permission checks in the AdminServer allow an authenticated client with insufficient privileges to invoke the `snapshot` and `restore` commands. The intended requirement is authentication and authorization on the root path (`/`) with **ALL** permission for these operations; however, affected versions permit invocation without that level of authorization. The primary risk is disclosure of cluster state via snapshots to a lesser-privileged client.

*   **Affected:** `org.apache.zookeeper:zookeeper` 3.9.0 through 3.9.3.
*   **Fixed:** 3.9.4 (ZOOKEEPER-4964 “check permissions individually during admin server auth”).
*   **Mitigations:**
    *   Disable both commands (`admin.snapshot.enabled`, `admin.restore.enabled`).
    *   Disable AdminServer (`admin.enableServer`).
    *   Ensure the root ACL is not open; note that ZooKeeper ACLs are not recursive.
    *   Upgrade to 3.9.4.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-58457
- https://github.com/apache/zookeeper
- https://lists.apache.org/thread/r5yol0kkhx2fzw22pxk1ozwm3oc6yxrx
- https://zookeeper.apache.org/doc/current/zookeeperSnapshotAndRestore.html
- https://zookeeper.apache.org/doc/r3.9.4/releasenotes.html
- https://zookeeper.apache.org/security.html#CVE-2025-58457
- http://github.com/apache/zookeeper/commit/71e173fcbcc9deb784081cf867bd045df3c32635
- http://www.openwall.com/lists/oss-security/2025/09/24/10
