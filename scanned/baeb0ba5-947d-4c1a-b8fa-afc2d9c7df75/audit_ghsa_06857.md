# [H] DSpace has possible Remote Code Execution (RCE)  through Velocity Templates used by LDN

## Summary
Severity: High
Advisory: GHSA-9x82-rm84-c6x7
CVE: CVE-2026-49832
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-08
Source: https://github.com/advisories/GHSA-9x82-rm84-c6x7
Type: github-advisory

## Affected
- Maven: `org.dspace:dspace-api` — affected >=8.0-rc1 <8.4
- Maven: `org.dspace:dspace-api` — affected >=9.0-rc1 <9.3
- Maven: `org.dspace:dspace-api` — affected >=10.0-rc1 <10.0

## Details
## Overview

Remote Code Execution (RCE) is possible via Velocity Templates used by DSpace for [COAR Notify/LDN messages](https://wiki.lyrasis.org/spaces/DSDOC9x/pages/379126679/COAR+Notify). _This vulnerability impacts DSpace versions 8.0 <= 8.3, 9.0 <= 9.2._ The attacker MUST already have DSpace administrator credentials in order to perform the attack.

This attack is related to the path traversal attack identified in [GHSA-9qm4-rh6w-pq5x](https://github.com/DSpace/DSpace/security/advisories/GHSA-9qm4-rh6w-pq5x) as it was the impactful part of the "proof-of-concept" attack chain.

## Impact

When chained with the LDN Path Traversal Attack identified in [GHSA-9qm4-rh6w-pq5x](https://github.com/DSpace/DSpace/security/advisories/GHSA-9qm4-rh6w-pq5x), it may be possible to execute Java directly from Velocity templates using reflection.  This is a very high impact vulnerability, but the attack can only be performed by a user that has DSpace Administrator privileges.  Disabling LDN (see below) removes all known attack paths.

Velocity is also used for email templating, but there is no known attack path via emails templates. Nonetheless, the patches below also apply to email templates.

## Patches

The fix is included in DSpace 8.4, 9.3 and 10.0.  Please upgrade to one of these versions or disable LDN (see below)

If users cannot upgrade immediately, it is possible to manually patch their DSpace backend. (No changes are necessary to the frontend.) A pull request exists which can be used to patch systems running DSpace 8.x or 9.x. 
* Pull request for 9.x: https://github.com/DSpace/DSpace/pull/12548  ([Downloadable patch file](https://github.com/DSpace/DSpace/pull/12548.patch))
* Pull request for 8.x: https://github.com/DSpace/DSpace/pull/12549  ([Downloadable patch file](https://github.com/DSpace/DSpace/pull/12549.patch))

### Apply the patch to a DSpace instance
If at all possible, DSpace project maintainers recommend disabling LDN (see below) or upgrading a DSpace site based on the upgrade instructions. However, if users are unable to do so, they can manually apply the above patches to their Space backend as follows:
1. Download the appropriate patch file to the machine where DSpace backend is running
2. From the `[dspace-src]` folder, apply the patch, e.g. `git apply [name-of-file].patch`
3. Now, update the application's DSpace site (based loosely on the Upgrade instructions). This generally involves three steps:
    1. Rebuild DSpace, e.g. `mvn -U clean package`  (This will recompile all DSpace backend code)
    2. Redeploy DSpace, e.g. `ant update`  (This will copy all newly built code to the application's installation directory). Depending on an application's setup users also may need to copy the updated "server" webapp over to their Tomcat webapps folder.
    3. Restart Tomcat (or runnable JAR)

## Workarounds
* In `dspace.cfg` or `local.cfg`, disable LDN (set `ldn.enabled=false`) if it is not crucial to the operation of the repository.  (NOTE: LDN is disabled by default, so many DSpace sites may not use this feature)
* Once users have patched theirr site or upgraded, they may safely enable LDN again.

## Resources
This vulnerability is similar to vulnerabilities reported by Velocity itself:
* Velocity 2.2. CVE: https://www.cve.org/CVERecord?id=CVE-2020-13936
    * This was patched in Velocity 2.3, and DSpace already includes this patch.

## Credits

Discovered & reported by Pablo Picurelli Ortiz (@superpegaso2703), cybersecurity student at Universidad Rey Juan Carlos. Reported as a possible attack combined with the LDN Path Traversal vulnerability.
Code fix developed by Kim Shepherd (@kshepherd) of The Library Code

## References
- https://github.com/DSpace/DSpace/security/advisories/GHSA-9x82-rm84-c6x7
- https://github.com/DSpace/DSpace/pull/12548
- https://github.com/DSpace/DSpace/pull/12549
- https://github.com/DSpace/DSpace
