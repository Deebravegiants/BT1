# [C] SQL injection in MilestoneFinder order method

## Summary
Severity: Critical (CVSS 9.9)
Program: GitLab
Weakness: SQL Injection
Reporter: jobert
State: resolved
Disclosed: 2018-04-27T02:20:24.581Z
CVE: CVE-2017-0914
Source: https://hackerone.com/reports/298176

## Details
The `MilestoneFinder` is a class used to find milestones based on group or project identifiers. The class is used in multiple controllers. It allows to filter based on state and can be used to order the result set. One of the uses can be found in the `Groups::MilestonesController`. When the **index** action is requested, the `milestones` method is called. Here's the first two lines of the method:

**app/controllers/groups/milestones_controller.rb**
```ruby
def milestones
    search_params = params.merge(group_ids: group.id)

    milestones = MilestonesFinder.new(search_params).execute
    # ...
```

This code takes all the parameters, merges the group found in the URL (that your account is authorized for) and calls the `execute` method. Here's the method:

**app/finders/milestone_finder.rb**
```ruby
  def execute
    return Milestone.none if project_ids.empty? && group_ids.empty?

    items = Milestone.all
    items = by_groups_and_projects(items)
    items = by_title(items)
    items = by_state(items)

    order(items)
  end
```

The `order` call on the last line is implemented as following: 

**app/finders/milestone_finder.rb**
```ruby
 def order(items)
    if params.has_key?(:order)
      items.reorder(params[:order])
    else
      order_statement = Gitlab::Database.nulls_last_order('due_date', 'ASC')
      items.reorder(order_statement)
    end
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/298176_
