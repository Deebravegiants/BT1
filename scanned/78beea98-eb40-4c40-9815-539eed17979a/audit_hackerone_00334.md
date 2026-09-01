# [C] Exfiltrate and mutate repository and project data through injected templated service

## Summary
Severity: Critical (CVSS 9.9)
Program: GitLab
Weakness: Improper Access Control - Generic
Reporter: jobert
State: resolved
Disclosed: 2019-03-05T00:09:55.389Z
Source: https://hackerone.com/reports/446585

## Details
The GitLab import feature contains a vulnerability that allows an attacker to import a project that creates a service template. Service templates can normally only be created by a GitLab instance Administrator. When a new project is created, service templates are automatically initialized for the project that is being created. Initializing and saving the service templates is handled in the `Projects::CreateService` class:

**app/services/projects/create_service.rb**
```ruby
# ...
def create_services_from_active_templates(project)
  Service.where(template: true, active: true).each do |template|
    service = Service.build_from_template(project.id, template)
    service.save!
  end
end
# ...
```

This means that when an attacker has created a templated service that is valid, any project created after that, will automatically install the attacker's service for that project. There are multiple attacks possible with this, which will be described in the Impact section of this report. Depending on the strategy the attacker takes, it may impact Confidentiality, Integrity, as well as Availability.

# Proof of concept
Attached you can find a tar file that injects a `MockCiService` as template to the GitLab instance: F377180. In order to manually reproduce this, follow the steps below.

1. Sign in as any user
1. Create a new project
1. Enable the CI service through Settings > Integrations
1. Export the project and download the export file
1. Extract the files, it'll contain a `project.json` file
1. Replace `"template":false` in the `services` array with `"template":true`
1. Replace `CiService` in the `services` array with `MockCiService`
1. Create a new tar file (`tar -zcvf service_template.tar.gz project.json VERSION project.bundle`)
1. Upload the tar file
1. Sign in as another user
1. Create another project
1. Immediately export the project and download the export file
1. Extract the files
1. Observe that the `project.json` file will contain the service created for the other project

# Additional, seemingly, less severe issues
When looking into this feature, it was also observed that an attacker can create custom attributes for a project. I noticed that custom project attributes can only be created by an instance Administrator. However, by specifying custom attributes in the `custom_attributes` array, a user can create custom project attributes for the project that is being created. Depending on how the custom attributes are used on the instance, this may have additional consequences.

## Impact

_Trimmed to 38 lines — full report: https://hackerone.com/reports/446585_
