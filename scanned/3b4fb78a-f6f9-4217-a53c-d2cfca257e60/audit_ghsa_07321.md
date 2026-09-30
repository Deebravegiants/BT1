# [M] DSpace: Path Traversal is possible through LDN message generation

## Summary
Severity: Medium
Advisory: GHSA-9qm4-rh6w-pq5x
CVE: CVE-2026-49833
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-07-08
Source: https://github.com/advisories/GHSA-9qm4-rh6w-pq5x
Type: github-advisory

## Affected
- Maven: `org.dspace:dspace-api` — affected >=8.0-rc1 <8.4
- Maven: `org.dspace:dspace-api` — affected >=9.0-rc1 <9.3
- Maven: `org.dspace:dspace-api` — affected >=10.0-rc1 <10.0

## Details
## Overview

A path traversal vulnerability is possible via the [COAR Notify / LDN](https://wiki.lyrasis.org/spaces/DSDOC9x/pages/379126679/COAR+Notify) service in DSpace. _This vulnerability impacts DSpace versions 8.0 <= 8.3, 9.0 <= 9.2._  The attacker MUST already have DSpace administrator credentials in order to perform the attack.

When reading a file input stream of an  "inbound pattern" / "template", used to generate an LDN message, the LDN class does not check for path traversal or restrict the templates to a known base path. This could allow an untrusted file from elsewhere in the file system (e.g. an export log, a bitstream path, a temporary file) to be read and interpreted as an Apache Velocity template.

Expected behaviour : Only the trusted templates kept in `$dspace.dir/config/ldn` should be allowed or used by LDN.

## Impact

On its own this seems a fairly low-impact problem: only DSpace Administrators can set LDN template names in services, and you typically need more access to manipulate files on the server.

However, this vulnerability was included as part of an attack chain that demonstrated the ability of a DSpace Administrator to put the malicious Velocity payload in a predictable place (e.g. temporary log file from a running process) and then have that file referenced as the template name in a new service.
 
This means it is possible (non-trivial, but proven) for an attacker with DSpace administrator credentials to either disclose information via a specially crafted Velocity template, or exploit another weakness in the DSpace Velocity implementation by executing arbitrary java code.


## Patches

The fix is included in DSpace 8.4, 9.3 and 10.0.  Please upgrade to one of these versions or disable LDN (see below)

If users cannot upgrade immediately, it is possible to manually patch their DSpace backend. (No changes are necessary to the frontend.) A pull request exists which can be used to patch systems running DSpace 8.x or 9.x. 
* Pull request for 9.x: https://github.com/DSpace/DSpace/pull/12552  ([Downloadable patch file](https://github.com/DSpace/DSpace/pull/12552.patch))
    * This 9.x patch file also resolves a similar [path traversal vulnerability in the Curation Task reporter](https://github.com/DSpace/DSpace/security/advisories/GHSA-v66x-68f2-pxf5)
* Pull request for 8.x: https://github.com/DSpace/DSpace/pull/12540  ([Downloadable patch file](https://github.com/DSpace/DSpace/pull/12540.patch))
    * This 8.x patch file also resolves a similar [path traversal vulnerability in the Curation Task reporter](https://github.com/DSpace/DSpace/security/advisories/GHSA-v66x-68f2-pxf5)

### Apply the patch to a DSpace
If at all possible, DSpace recommends disabling LDN (see below) or upgrading the user's DSpace site based on the upgrade instructions. However, if users are unable to do so, they can manually apply the above patches to their DSpace backend as follows:
1. Download the appropriate patch file to the machine where DSpace backend is running
2. From the `[dspace-src]` folder, apply the patch, e.g. `git apply [name-of-file].patch`
3. Now, update the DSpace site (based loosely on the Upgrade instructions). This generally involves three steps:
    1. Rebuild DSpace, e.g. `mvn -U clean package`  (This will recompile all DSpace backend code)
    2. Redeploy DSpace, e.g. `ant update`  (This will copy all newly built code to their installation directory). Depending on their setup they also may need to copy the updated "server" webapp over to their Tomcat webapps folder.
    3. Restart Tomcat (or runnable JAR)

## Workarounds
* In `dspace.cfg` or `local.cfg`, disable LDN (set `ldn.enabled=false`) if it is not crucial to the operation of the repository.  (NOTE: LDN is disabled by default, so many DSpace sites may not use this feature)
* Once users have patched their site or upgraded, they may safely enable LDN again.

## Credits
Discovered & reported by Pablo Picurelli Ortiz (@superpegaso2703), cybersecurity student at Universidad Rey Juan Carlos.
Code fix developed by Kim Shepherd (@kshepherd) of The Library Code

## References
- https://github.com/DSpace/DSpace/security/advisories/GHSA-9qm4-rh6w-pq5x
- https://github.com/DSpace/DSpace/pull/12540
- https://github.com/DSpace/DSpace
