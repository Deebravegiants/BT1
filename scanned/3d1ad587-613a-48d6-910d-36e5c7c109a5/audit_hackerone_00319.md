# [M] Custom Field Attributes may be created and updated for customers with Custom Field Trial enabled

## Summary
Severity: Medium (CVSS 5.2)
Program: HackerOne
Weakness: Improper Access Control - Generic
Reporter: jobert
State: resolved
Disclosed: 2019-07-05T16:54:45.276Z
Source: https://hackerone.com/reports/634679

## Details
The Custom Field feature is currently only available for customers on the Enterprise product edition. A trial period can be given by enabling the `custom-fields-trial` feature for programs who are not on that product edition (yet). However, when enabling this feature, the incorrect ordering of an ACL causes a vulnerability that allows anyone that can access the program to create and update Custom Field Attributes. This also works for private programs with an External Program Profile.

# Steps to reproduce
Below are two regression specs. Both of these specs currently fail on `develop` and `master`.

```ruby
describe '#can_manage_custom_fields?' do
  # ... other specs for this ACL ...
  subject { Pavlov.can? :manage_custom_fields, team, user }

  let(:user) { create :user }

  context 'with trial feature enabled' do
    before { create :feature, teams: [team], key: Feature::CUSTOM_FIELDS_TRIAL }

    context 'with a private program' do
      let(:team) { create :team, :soft_launched }

      context 'without a published external program' do
        # adding `user` as an invited hacker to the team
        before do
          Commands::WhitelistedReporters::Create.interact \
            user: user,
            team: team,
            source: WhitelistedReporter::SOURCE_UNKNOWN_INVITE
        end

        it { is_expected.to eq false }
      end

      context 'with a published external program' do
        before { create :external_program, team: team }

        it { is_expected.to eq false }
      end
    end
  end
end
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/634679_
