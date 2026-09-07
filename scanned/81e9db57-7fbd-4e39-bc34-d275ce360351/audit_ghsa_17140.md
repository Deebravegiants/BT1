# [M] Pinned entity creation form shows wrong data

## Summary
Severity: Medium
Advisory: GHSA-vxq2-p937-3px3
CVE: CVE-2023-45824
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-03-25
Source: https://github.com/advisories/GHSA-vxq2-p937-3px3
Type: github-advisory

## Affected
- Packagist: `oro/platform` — affected >=5.1.0 <5.1.4
- Packagist: `oro/platform` — affected >=5.0.0
- Packagist: `oro/platform` — affected >=4.2.0

## Details
### Impact

Logged in user can access page state data of pinned pages of other users by pageId hash.


### Patch

```patch
--- src/Oro/Bundle/NavigationBundle/Controller/Api/PagestateController.php
+++ src/Oro/Bundle/NavigationBundle/Controller/Api/PagestateController.php
@@ -158,6 +158,13 @@
             AbstractPageState::generateHash($this->get('request_stack')->getCurrentRequest()->get('pageId'))
         );
 
+        if ($entity) {
+            $entity = $this->getEntity($entity->getId());
+        }
+        if (!$entity) {
+            return $this->handleNotFound();
+        }
+
         return $this->handleView($this->view($this->getState($entity), Response::HTTP_OK));
     }
 
```

## References
- https://github.com/oroinc/platform/security/advisories/GHSA-vxq2-p937-3px3
- https://nvd.nist.gov/vuln/detail/CVE-2023-45824
- https://github.com/oroinc/platform/commit/cf94df7595afca052796e26b299d2ce031e289cd
- https://github.com/oroinc/platform
