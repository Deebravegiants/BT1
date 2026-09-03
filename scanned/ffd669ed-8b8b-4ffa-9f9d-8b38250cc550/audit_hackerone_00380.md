# [C] Command injection by overwriting authorized_keys file through GitLab import

## Summary
Severity: Critical (CVSS 9.9)
Program: GitLab
Weakness: Command Injection - Generic
Reporter: jobert
State: resolved
Disclosed: 2018-04-27T02:20:49.927Z
CVE: CVE-2017-0915
Source: https://hackerone.com/reports/298873

## Details
The `Projects::GitlabProjectsImportService` contains a vulnerability that allows an attacker to write files to arbitrary directories on the server. This leads to an arbitrary command execution vulnerability by overwriting the `authorized_keys` file. To reproduce, sign in to a GitLab instance that has GitLab import enabled. This is enabled by default, so I'd assume that this vulnerability applies to most GitLab instances. I've installed my GitLab instance through Omnibus.

Next up, intercept your network traffic and upload a GitLab import file. Observe the following request being made to the server:

**Request**
```
POST /import/gitlab_project HTTP/1.1
Host: gitlab-instance
...

------WebKitFormBoundaryA0TxBpQRLhL4lJQN
Content-Disposition: form-data; name="path"
test
------WebKitFormBoundaryA0TxBpQRLhL4lJQN
Content-Disposition: form-data; name="namespace_id"

1
------WebKitFormBoundaryA0TxBpQRLhL4lJQN
Content-Disposition: form-data; name="file"; filename="2017-12-17_02-20-093_root_test_export.tar.gz"
Content-Type: application/x-gzip

<file data>
```

Now take a closer look at the code that is being executed when this endpoint is hit:

**app/services/projects/gitlab_project_import_service.rb**
```ruby
# This service is an adapter used to for the GitLab Import feature, and
# creating a project from a template.
# The latter will under the hood just import an archive supplied by GitLab.
module Projects
  class GitlabProjectsImportService
    # ...

    def execute
      FileUtils.mkdir_p(File.dirname(import_upload_path))
      FileUtils.copy_entry(file.path, import_upload_path)
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/298873_
