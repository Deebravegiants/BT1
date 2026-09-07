# [M] Authorization Bypass in I hate money

## Summary
Severity: Medium
Advisory: GHSA-67j9-c52g-w2q9
CVE: CVE-2020-15120
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2020-07-27
Source: https://github.com/advisories/GHSA-67j9-c52g-w2q9
Type: github-advisory

## Affected
- PyPI: `ihatemoney` — affected >=0 <4.1.5

## Details
### Impact
An authenticated member of one project can modify and delete members of another project, without knowledge of this other project's private code. This can be further exploited to access all bills of another project without knowledge of this other project's private code.

With the default configuration, anybody is allowed to create a new project. An attacker can create a new project and then use it to become authenticated and exploit this flaw. As such, the exposure is similar to an unauthenticated attack, because it is trivial to become authenticated.

### Patches
```diff
 ihatemoney/models.py | 4 ++--
 1 file changed, 2 insertions(+), 2 deletions(-)

diff --git a/ihatemoney/models.py b/ihatemoney/models.py
index fe7b519..5691c75 100644
--- a/ihatemoney/models.py
+++ b/ihatemoney/models.py
@@ -380,7 +380,7 @@ class Person(db.Model):
         def get_by_name(self, name, project):
             return (
                 Person.query.filter(Person.name == name)
-                .filter(Project.id == project.id)
+                .filter(Person.project_id == project.id)
                 .one()
             )
 
@@ -389,7 +389,7 @@ class Person(db.Model):
                 project = g.project
             return (
                 Person.query.filter(Person.id == id)
-                .filter(Project.id == project.id)
+                .filter(Person.project_id == project.id)
                 .one()
             )
 
```

### Workarounds

To limit the impact, it is possible to disable public project creation by setting `ALLOW_PUBLIC_PROJECT_CREATION = False` in the configuration (see [documentation](https://ihatemoney.readthedocs.io/en/latest/configuration.html)). Existing users will still be able to exploit the flaw, but this will prevent an external attacker from creating a new project.

### For more information

`Person.query.get()` and `Person.query.get_by_name()` were mistakenly running a database join on the Project table without constraining the result.

As a result, `Person.query.get(42, "projectfoo")` would return the Person with id=42, even if it is not associated to the project "projectfoo".  The only condition is that "projectfoo" must exist.

This flaw can be exploited in several places:

1) API: PUT requests to `/api/projects/<project>/members/<personID>` will succeed even though `<personID>` is not a member of `<project>`.

   This allows an authenticated attacker to alter the state of a member (name, weight, activated) in any project.  In addition, the altered member will no longer be associated with its original project but will be associated to the attacker project instead, breaking many features of IHateMoney.  For instance, bills referencing the altered member will no longer be visible in the original project.

   This causes an additional information disclosure and loss of integrity on bills: the attacker will now be able to see, edit and delete bills belonging to the altered member, because IHateMoney now believes that these bills are associated to the attacker project through the altered member.

   For instance, assume that `Person(id=42)` is a member of project "targetProject", and that the attacker has access to another project "attackerProject" with the private code "attackerPassword".  The attacker can modify `Person(id=42)` with this command:

     $ curl -X PUT -d "name=Pwn3d&activated=1" --basic -u attackerProject:attackerPassword http://$SERVER/api/projects/attackerProject/members/42

   The attacker can now see, edit and delete bills paid by `Person(id=42)` by simply browsing to http://$SERVER/attackerProject/

2) Editing a member through the web interface at `/<project>/members/<personID>/edit` will succeed even though `<personID>` is not a member of `<project>`.

   This is very similar to the PUT exploit.  Reusing the same example, the attacker needs to login to its "attackerProject" project with the private code "attackerPassword".  It can then alter the state of `Person(id=42)` by accessing the edit form at the following URL:

     http://$SERVER/attackerProject/members/42/edit

   Again, as a result of the alteration, the altered member will become associated to the project "attackerProject", resulting in the same information disclosure and loss of integrity on bills.

3) API: DELETE requests to `/api/projects/<project>/members/<personID>` will similarly allow to delete the member `<personID>` even if it belongs to a different project than `<project>`.

     $ curl -X DELETE --basic -u attackerProject:attackerPassword http://$SERVER/api/projects/attackerProject/members/42

   The impact is less serious than with PUT, because DELETE only deactivates a member (it does not really delete it).

All these exploits require authentication: an attacker needs to know a valid project name and its associated "private code".  Once this requirement is fullfilled, the attacker can exploit this flaw to alter the state of members in any other project, without needing to know the target project name or its private code.

`Person.query.get_by_name()` suffers from the same issue as `Person.query.get()`.  It has an additional issue: if multiple Person objects with the same name exist (this is possible if they are associated to different projects), `get_by_name()` will crash with `MultipleResultsFound` because of the call to `one()`.

However, since `Person.query.get_by_name()` is currently not used anywhere in IHateMoney, the bug affecting this function has no impact and is not exploitable.

## References
- https://github.com/spiral-project/ihatemoney/security/advisories/GHSA-67j9-c52g-w2q9
- https://nvd.nist.gov/vuln/detail/CVE-2020-15120
- https://github.com/spiral-project/ihatemoney/commit/8d77cf5d5646e1d2d8ded13f0660638f57e98471
- https://github.com/pypa/advisory-database/tree/main/vulns/ihatemoney/PYSEC-2020-264.yaml
- https://github.com/spiral-project/ihatemoney
