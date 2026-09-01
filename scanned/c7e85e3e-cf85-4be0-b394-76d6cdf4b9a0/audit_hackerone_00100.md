# [M] RepositoryPipeline allows importing of local git repos

## Summary
Severity: Medium (CVSS 6.5)
Program: GitLab
Weakness: Improper Access Control - Generic
Reporter: vakzz
State: resolved
Disclosed: 2022-11-04T03:43:34.930Z
Source: https://hackerone.com/reports/1685822

## Details
### Summary

When importing a project via the BulkImports, the response field `httpUrlToRepo` from the client is used to fetch the repo:

https://gitlab.com/gitlab-org/gitlab/-/blob/v15.3.1-ee/lib/bulk_imports/projects/pipelines/repository_pipeline.rb#L17
```ruby
        def load(context, data)
          url = data['httpUrlToRepo']
          return unless url.present?

          url = url.sub("://", "://oauth2:#{context.configuration.access_token}@")
          project = context.portable

          Gitlab::UrlBlocker.validate!(url, allow_local_network: allow_local_requests?, allow_localhost: allow_local_requests?)

          project.ensure_repository
          project.repository.fetch_as_mirror(url)
        end
```

`Gitlab::UrlBlocker.validate` is called, but since no schemas are passed in it allows any (such as file) so long as the rest of the url is valid.

This means that if a url such as `file://aw.rs/var/opt/gitlab/git-data/repositories/@hashed/b1/74/b174103b399555239923697fbe124faa61de4d441bd5c5678275eb0a5a27a562.git` is supplied, this will end up being used by git fetch, eg:

```bash
$ git fetch file://aw.rs/var/opt/gitlab/git-data/repositories/@hashed/b1/74/b174103b399555239923697fbe124faa61de4d441bd5c5678275eb0a5a27a562.git
fatal: '/var/opt/gitlab/git-data/repositories/@hashed/b1/74/b174103b399555239923697fbe124faa61de4d441bd5c5678275eb0a5a27a562.git' does not appear to be a git repository
fatal: Could not read from remote repository.

Please make sure you have the correct access rights
and the repository exists.
```

This allows an attacker to import any local repository that the current machine has access to if the path is known.

The storage path for projects in gitlab is just based on a configurable folder combined with a bucketed sha2 hash of  the id, eg for project 38006449 the `Digest::SHA2.hexdigest("38006449")` is  `b174103b399555239923697fbe124faa61de4d441bd5c5678275eb0a5a27a562` so the path will be at `@hashed/b1/74/b174103b399555239923697fbe124faa61de4d441bd5c5678275eb0a5a27a562.git`.

This can then be used to import any gitlab repository via the project id by calculating the path, such as the gitlab ctf project!

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1685822_
